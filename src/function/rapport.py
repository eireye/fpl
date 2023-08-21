import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import openpyxl
import json
import plotly.graph_objs as go
import plotly.offline as pyo

import lagvalg
import xp
import plots
from IPython.core.display import HTML, display


from lagvalg import *
from plots import *


def rapport(data, gameweek):
    """
    Generate an HTML report for a given Fantasy Premier League (FPL) gameweek.

    Parameters:
    - data (pandas DataFrame): The FPL data for the current season.
    - gameweek (int): The gameweek number for which to generate the report.

    Returns:
    - None

    The report includes:
    - A title and introduction text
    - Any transfers made in/out for the gameweek
    - The user's starting lineup with captain and vice-captain highlighted
    - The total expected points for the starting lineup
    - The user's bench lineup
    - A graph comparing the user's actual points to their expected points for the gameweek
    """
    # 1. Set up multiple variables to store the titles, text within the report
    page_title_text = 'FPL rapport'
    title_text = f'Rapport for gameweek {gameweek}'

    startlagtekst = f'Informasjon for gameweek {gameweek}'
    
    
    

    transfer_in_list = transfer_in(data, gameweek)
    transfer_out_list = transfer_out(data, gameweek)

    if transfer_in_list or transfer_out_list:
        bytter = "<h2>Bytter:</h2>\n\n"
    if transfer_in_list:
        bytter += f"<p>Bytt inn: {' | '.join(transfer_in_list)}</p>\n\n"
    if transfer_out_list:
        bytter += f"<p>Bytte ut: {' | '.join(transfer_out_list)}</p>\n\n"
    else:
        bytter = "<p>Ingen bytter.</p>"

    # bytter = f"Bytt inn: <br>{', '.join(transfer_in(data,gameweek))}<br><br>Bytte ut: <br>{', '.join(transfer_out(data,gameweek))}"

    benktekst = f"Her er benken for Gameweek {gameweek}"
    graftekst = "Graf med oversikt over faktiske poeng og expected points"
    graftekst2= "Graf med oversikt over Kapteinens faktiske poeng og expected poeng"
    sum_expected = round(startlag(data, gameweek)["xP"].sum(), 0)
    sum_expected_points_tekst =  f"Forventet poeng med dette laget er: {sum_expected}"

# format the `sum_expected_points_tekst` text with a larger font size and green color
    sum_expected_points_html = f'<span style="font-size: 1.3em; color: green;">{sum_expected_points_tekst}</span>'

    data2 = startlag(data, gameweek).drop(['buy_price', 'sell_price', 'lineup', 'captain', 'vicecaptain'], axis=1)

# rename the columns
    data2 = data2.rename(columns={'name': 'Navn', 'team': 'Lagnavn', 'pos': 'Posisjon', 'xP': 'Forventet poeng'})
    data2_highlight = data2.style.format({'Forventet poeng': '{:.0f}'}).highlight_max(subset=['Forventet poeng'], color='green')
    
        # Generate the HTML code for the plot
    plot_html = poeng_vs_expected_graf(expected_poeng())
    #plot_html2 = poeng_vs_expected_graf(expected_poeng_c())
    
    captain = startlag(data,gameweek).loc[startlag(data,gameweek)['captain'] == 1, ['name', 'team']].squeeze()
    vice_captain = startlag(data,gameweek).loc[startlag(data,gameweek)['vicecaptain'] == 1, ['name', 'team']].squeeze()
    captain_html = (
    "<p>Kaptein: {} ({})</p>"
    "<p>Vice-captain: {} ({})</p>").format(captain['name'], captain['team'], vice_captain['name'], vice_captain['team'])

    data3 = benklag(data, gameweek).drop(['buy_price', 'sell_price',  'bench'], axis=1)
    data3 = data3.rename(columns={'name': 'Navn', 'team': 'Lagnavn', 'pos': 'Posisjon', 'xP': 'Forventet poeng'})
    data3_html = data3.style.format({'Forventet poeng': '{:.0f}'}).to_html(classes='grey', index=False)



   

    html = f'''
<!DOCTYPE html>
<html>
    <head>
        <title>{page_title_text}</title>
        
        <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.5;
                    padding: 20px;
                    background-color: #1F1F1F;
                    color: #EFEFEF;
                }}
                h1 {{
                    font-size: 2em;
                    text-align: center;
                    margin-bottom: 20px;
            }}
            h2 {{
                font-size: 1.5em;
                margin-top: 30px;
                margin-bottom: 20px;
                border-bottom: 2px solid #6E7F80;
                padding-bottom: 5px;
            }}
            h3 {{
                font-size: 1.2em;
                margin-top: 30px;
                margin-bottom: 20px;
                border-bottom: 1px solid #6E7F80;
                padding-bottom: 5px;
            }}
            p {{
                font-size: 1.1em;
                margin-bottom: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #6E7F80;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #3A3A3A;
                color: #EFEFEF;
            }}
            .green {{
                background-color: #2E8B57;
                color: #EFEFEF;
            }}
            .red {{
                background-color: #FF6347;
                color: #EFEFEF;
            }}
            .orange {{
                background-color: #FFA500;
                color: #EFEFEF;
            }}

            .flex-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
            }}
            .flex-item {{
                width: 40%;  /* you can adjust this as needed */
                margin-bottom: 20px;
            }}
        
        </style>
    </head>
    <body>
        <h1>{title_text}</h1>
        <h2>{startlagtekst}</h2>
        
        <div class="flex-container">
            <div class="flex-item">
            <h3>Startlag</h3>
                {data2_highlight.to_html(classes='green', index=False)}
            </div>
            <div class="flex-item">
            <h3>Benk</h3>
                {data3_html}
                <h3>Kaptein og Visekaptein</h3>
                {captain_html}  
                <p>{sum_expected_points_html}</p>
                {bytter}
                
            </div>
        </div>
        <h2>{graftekst}</h2>
        
        {plot_html}
       
            
    </body>
</html>
'''




# Display the HTML in the notebook
    display(HTML(html))
# 3. Write the html string as an HTML file
    with open('../output/html_report.html', 'w') as f:
        f.write(html)
