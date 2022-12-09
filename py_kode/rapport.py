import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests

latest_optimal_plan_data = pd.read_csv("output/optimal_plan_regular.csv")

# Lage grafen som brukes i rapporten


# lager en rapport med graf og flere tabeller

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

def transfer_in(data, gameweek):
   transferin= data.loc[(data["week"]==gameweek)& (data['transfer_in']== 1), ["name","team"]].values[0]
   return str(transferin)

def transfer_out(data, gameweek):
   transferout= data.loc[(data["week"]==gameweek)& (data['transfer_out']== 1), ["name","team"]].values[0]
   return str(transferout)

def rapport(data, gameweek):    
    # 1. Set up multiple variables to store the titles, text within the report
    page_title_text='FPL rapport'
    title_text = 'Eiriks FPL rapport'
    introtext = f'Hei, her er rapport for gameweek {gameweek}'
    startlagtekst = 'Startlag: Kapteinen har lagt inn poeng som regnes med i tabellen'
    bytter = f"Bytt inn:{transfer_in(data,gameweek)}. Bytte ut:{transfer_out(data,gameweek)}"
    benktekst= "Her er benken din"
    graftekst = "Graf med overikst over faktiske poeng og expected points"
    sum_expected = round(startlag(data,gameweek)["xP"].sum(),0)
    sum_expected_points_tekst = f"Forventet poeng med dette laget er : {sum_expected}"

    # 2. Combine them together using a long f-string
    html = f'''
        <html>
            <head>
                <title>{page_title_text}</title>
            </head>
            <body>
                <h1>{title_text}</h1>
                <p>{introtext}</p>
                <p>{bytter}</p>
                <h2>{startlagtekst}</h2>
                {startlag(data,gameweek).to_html()}
                <p>{sum_expected_points_tekst}</p>
                <h3>{benktekst}</h3>
                {benklag(data, gameweek).to_html()}
                <h4>{graftekst}</h4>
                <img src='chart.png' width="700">
            </body>
        </html>
        '''
    # 3. Write the html string as an HTML file
    with open('output/html_report.html', 'w') as f:
        f.write(html)
    
rapport(latest_optimal_plan_data, 17)