import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import openpyxl


def get_team_points(week, id):
    team_id = id
    current_week = str(week)
    url = "https://fantasy.premierleague.com/api/entry/"+team_id+"/event/"+current_week+"/picks/"
    my_team_data = requests.get(url)
    my_team_data = my_team_data.json()
    Week.append(current_week)
    points.append(my_team_data["entry_history"]["points"])


def points_without_cap (data, next_gw):
    """Gir summen av xP uten kapteinen, kan gjøres bedre etterhvert tenker jeg"""
    return data.loc[(data["week"]==next_gw)& (data['lineup']== 1) & (data["captain"]!=1), ["xP"]].sum()


def double_captain_points(data, next_gw):
    """Gir sum av kapteinens totalepoeng for gitte uke. Sett at dataframe inneholder week, xP og captain kolonner"""
    data.loc[(data["captain"] ==1) & (data["week"]==next_gw), ["xP"]]*2
    return data.loc[(data["captain"] ==1) & (data["week"]==next_gw), ["xP"]]*2


def expected_points(data, next_gw):
    """Funksjon som bruker to andre funksjoner for å hente summen av xP for Next_gw i datasett"""
    doubled_captain= double_captain_points(data, next_gw)
    
    expected_points= points_without_cap(data, next_gw)

    return int(expected_points.sum() + doubled_captain.sum())


def add_new_row(data, gameweek):
    """Legger til ny row med data"""
    # if (data['Uke'].eq(f'{gameweek}')).any() == False:
    new_row = {'Uke':f"{gameweek}", 'Poeng':0, #get_team_points(gameweek, 2821496), 
    'xP':expected_points(latest_optimal_plan_data, gameweek)}
    new_row2= pd.Series(new_row)
    #append row to the dataframe
    data.loc[len(data.index)] = new_row2
    return data

def get_team_points(week, id):
    team_id = str(id)
    current_week = str(week)
    url = "https://fantasy.premierleague.com/api/entry/"+team_id+"/event/"+current_week+"/picks/"
    my_team_data = requests.get(url)
    my_team_data = my_team_data.json()
    return my_team_data["entry_history"]["points"]

def startlag(data, gameweek):
   """Henter startelleveren ut i fra optimal plan csv"""
   startellever= data.loc[(data["week"]==gameweek)& (data['lineup']== 1)]
   startellever2 = startellever.drop(["Unnamed: 0","week", "type", "xMin", "bench", "transfer_in", "transfer_out"], axis = 1)
   startellever2.loc[startellever2["captain"]==1, ["xP"]] *=2
   return startellever2

def benklag(data, gameweek):
   benk = data.loc[(data["week"]==gameweek)& (data['bench']>= 1)]
   benk2 = benk.drop(["Unnamed: 0","week", "type", "xMin", "captain", "vicecaptain","lineup", "transfer_in", "transfer_out"], axis = 1)
   
   return benk2.sort_values(by=['bench'])

# def transfer_in(data, gameweek):
#    transferin= data.loc[(data["week"]==gameweek)& (data['transfer_in']== 1), ["name","team"]].values[0]
#    return str(transferin)

# def transfer_out(data, gameweek):
#    transferout= data.loc[(data["week"]==gameweek)& (data['transfer_out']== 1), ["name","team"]].values[0]
#    return str(transferout)

# def transfer_in(data, gameweek):
#    transferin = data.loc[(data["week"]==gameweek) & (data['transfer_in']== 1), ["name","team"]]
#    return [f"{x[0]} {x[1]}" for x in transferin.values]

# def transfer_out(data, gameweek):
#    transferout = data.loc[(data["week"]==gameweek) & (data['transfer_out']== 1), ["name","team"]]
#    return [f"{x[0]} {x[1]}" for x in transferout.values]

def transfer_in(data, gameweek):
   transferin = data.loc[(data["week"]==gameweek) & (data['transfer_in']== 1), ["name","team"]]
   return [f"{x[0]} ({x[1]})" for x in transferin.values]

def transfer_out(data, gameweek):
   transferout = data.loc[(data["week"]==gameweek) & (data['transfer_out']== 1), ["name","team"]]
   return [f"{x[0]} ({x[1]})" for x in transferout.values]

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
    title_text = 'Eiriks FPL rapport'
    introtext = f'Hei, her er rapport for gameweek {gameweek}'
    startlagtekst = 'Startlag der kapteinen har fått poengene sine doblet'
    inntekst = 'bytt inn'
    uttekst = "bytt ut"



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

    benktekst = "Her er benken din"
    graftekst = "Graf med oversikt over faktiske poeng og expected points"
    sum_expected = round(startlag(data, gameweek)["xP"].sum(), 0)
    sum_expected_points_tekst =  f"Forventet poeng med dette laget er: {sum_expected}"

# format the `sum_expected_points_tekst` text with a larger font size and green color
    sum_expected_points_html = f'<span style="font-size: 1.3em; color: green;">{sum_expected_points_tekst}</span>'

    data2 = startlag(data, gameweek).drop(['buy_price', 'sell_price', 'lineup', 'captain', 'vicecaptain'], axis=1)

# rename the columns
    data2 = data2.rename(columns={'name': 'Navn', 'team': 'Lagnavn', 'pos': 'Posisjon', 'xP': 'Forventet poeng'})
    data2_highlight = data2.style.format({'Forventet poeng': '{:.0f}'}).highlight_max(subset=['Forventet poeng'], color='green')
    
        # Generate the HTML code for the plot
    #plot_html = poeng_vs_expected_graf(df_poeng_xP, gameweek)
    
    captain = startlag(data,gameweek).loc[startlag(data,gameweek)['captain'] == 1, ['name', 'team']].squeeze()
    vice_captain = startlag(data,gameweek).loc[startlag(data,gameweek)['vicecaptain'] == 1, ['name', 'team']].squeeze()
    captain_html = (
    "<p>Dette er kapteinen: {} ({})</p>"
    "<p>Dette er vice-captain: {} ({})</p>").format(captain['name'], captain['team'], vice_captain['name'], vice_captain['team'])




   

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
        </style>
    </head>
    <body>
        <h1>{title_text}</h1>
        <p>{introtext}</p>
        {bytter}
        <h2>{startlagtekst}</h2>
        {captain_html}
        {data2_highlight.to_html(classes='green', index=False)}
        <p>{sum_expected_points_html}</p>
        <h3>{benktekst}</h3>
        {benklag(data, gameweek).to_html(classes='grey', index=False)}
        <h2>{graftekst}</h2>
        {"TEST"}
    </body>
</html>
'''


# 3. Write the html string as an HTML file
    with open('../output/html_report.html', 'w') as f:
        f.write(html)


import plotly.graph_objs as go
import plotly.offline as pyo

def poeng_vs_expected_graf(data, gameweek):
    # Calculate the mean of the "Poeng" column
    poeng_mean = data[data["Poeng"] != 0]["Poeng"].mean()
    
    # Calculate the mean of the "xP" column, excluding zero values
    xp_mean = data[data["xP"] != 0]["xP"].mean()
    
    # Create a line plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Uke"], y=data["Poeng"], mode="lines+markers", name="Faktisk poeng"))
    fig.add_trace(go.Scatter(x=data[data["xP"] != 0]["Uke"], y=data[data["xP"] != 0]["xP"], mode="lines+markers", name="Forventet poeng"))
    fig.add_shape(type="line", x0=data["Uke"].min(), y0=poeng_mean, x1=data["Uke"].max(), y1=poeng_mean, line=dict(color="blue", width=5, dash="dot"), name="Gjennomsnitt faktisk poeng")
    fig.add_shape(type="line", x0=data["Uke"].min(), y0=xp_mean, x1=data["Uke"].max(), y1=xp_mean, line=dict(color="red", width=5, dash="dot"), name="Gjennomsnitt forventet poeng")
    
    fig.add_annotation(x=data["Uke"].max(), y=poeng_mean, text=f"Gjennomsnitt faktisk poeng: {poeng_mean:.2f}", showarrow=False, font=dict(size=12, color="black"), yshift=10)
    fig.add_annotation(x=data["Uke"].max(), y=xp_mean, text=f"Gjennomsnitt forventet poeng: {xp_mean:.2f}", showarrow=False, font=dict(size=12, color="black"), yshift=10)
    fig.update_layout(
        title="Poeng vs. forventet poeng for hver uke",
        xaxis_title="Uke",
        yaxis_title="Poeng",
        legend=dict(
            x=1.0,
            y=1.0,
            bgcolor="rgba(240, 240, 240, 240)",
            bordercolor="grey",
            borderwidth=1,
            font=dict(size=16)
        ),
        plot_bgcolor="rgb(175, 175, 175)",
        paper_bgcolor="rgb(175, 175, 175)",

        height=800,
        font=dict(size=16)
        ,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    
    # Generate the HTML code for the plot
    plot_html = pyo.plot(fig, output_type='div')
    
    # Return the HTML code as a string
    return plot_html


latest_optimal_plan_data = pd.read_csv("../output/optimal_plan_regular.csv")


