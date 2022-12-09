
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests

latest_optimal_plan_data = pd.read_csv("output/optimal_plan_regular.csv")

xP =[]
for i in range(1,17):
    xP.append(0)
xP

team_id = "2821496"
current_week = "7"
url = "https://fantasy.premierleague.com/api/entry/"+team_id+"/event/"+current_week+"/picks/"
my_team_data = requests.get(url)
my_team_data = my_team_data.json()
my_team_data["entry_history"]["points"]

points=[]
Week=[]
def get_team_points(week, id):
    team_id = id
    current_week = str(week)
    url = "https://fantasy.premierleague.com/api/entry/"+team_id+"/event/"+current_week+"/picks/"
    my_team_data = requests.get(url)
    my_team_data = my_team_data.json()
    Week.append(current_week)
    points.append(my_team_data["entry_history"]["points"])

for i in range(1,17):
    get_team_points(i, "2821496")
faktiske_poeng={"Uke":Week, "Poeng":points}

df_poeng_xP = pd.DataFrame(faktiske_poeng)
df_poeng_xP.set_index("Uke", inplace=False)
df_poeng_xP["xP"]= xP
df_poeng_xP.to_csv("output/Poengsammendrag")

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

def poeng_vs_expected_graf(data, gameweek):
    
            
       sns.set_theme(style="white", palette="pastel")
       f, ax = plt.subplots(figsize=(10, 10))
       # Lage funksjon som lager datafilen som brukes
       # data = df_poeng_xp()
       sns.despine(left=True, bottom=False)
        # plot line graph
       sns.set(rc={"figure.figsize":(10,10)})
       ax = sns.lineplot(data=add_new_row(data, gameweek), x= "Uke", y="Poeng" ,marker="*")
       ax1 = sns.lineplot(data=add_new_row(data, gameweek), x= "Uke", y="xP" ,marker="*")
       ax.set(title="Poeng for hver uke")# label points on the plot
       for x, y in zip(add_new_row(data, gameweek)["Uke"], add_new_row(data, gameweek)["Poeng"]):
        # the position of the data label relative to the data point can be adjusted by adding/subtracting a value from the x &/ y coordinates
              plt.text(x = x, # x-coordinate position of data label
              y = y, # y-coordinate position of data label, adjusted to be 150 below the data point
              s = "{:.0f}".format(y), # data label, formatted to ignore decimals
              color = "purple") # set colour of line
       for x, y in zip(add_new_row(data, gameweek)["Uke"], add_new_row(data, gameweek)["xP"]):
        # the position of the data label relative to the data point can be adjusted by adding/subtracting a value from the x &/ y coordinates
              plt.text(x = x, # x-coordinate position of data label
              y = y, # y-coordinate position of data label, adjusted to be 150 below the data point
              s = "{:.0f}".format(y), # data label, formatted to ignore decimals
              color = "purple") # set colour of line

       plt.savefig('output/chart.png')

poeng_vs_expected_graf(df_poeng_xP, 17)