import pandas as pd
import json
import requests


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
    sum = float((expected_points.sum() + doubled_captain.sum()).iloc[0])
    sum1 = int(round(sum,0))

    return sum1
    

def write_data(df,gw):
    data = []
    try:
        # Try to load existing data
        with open('xp_data.json', 'r') as file:
            
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/invalid, start with empty list
        pass

    # Check if gameweek data already exists
    for i, item in enumerate(data):
        if item.get('Gameweek') == gw:
            confirmation = input(f'Data for Gameweek {gw} finnes allerede. Overskrive? (j/n): ')
            if confirmation.lower() == 'j':
                data[i] = {
                    'Gameweek': gw,
                    'XP': expected_points(df,gw)
                }
            else:
                print(f"Data ikke overskrevet for gameweek {gw}")
                return  # Exit the function immediately

            break
    else:  
        # Append new data if it doesn't already exist
        data.append({
            'Gameweek': gw,
            'XP': expected_points(df,gw)
        })

    # Write data back to file
    with open('xp_data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Global dictionary to store data
week_points_dict = {}


def get_team_points(week, id):
    team_id = str(id)
    current_week = str(week)
    url = "https://fantasy.premierleague.com/api/entry/"+team_id+"/event/"+current_week+"/picks/"
    my_team_data = requests.get(url)
    my_team_data = my_team_data.json()

    try:
        points_value = my_team_data["entry_history"]["points"]
        week_points_dict[current_week] = points_value
    except KeyError:
        pass


def save_data_to_json():
    # Convert the week_points_dict to a list of dictionaries
    data = [{'Gameweek': w, 'Points': p} for w, p in week_points_dict.items()]
    
    # Write the data to a JSON file
    with open("poeng_data.json", 'w') as file:
        json.dump(data, file, indent=4)


def expected_poeng():
    df_poeng = pd.read_json('poeng_data.json')
  
    df_xp = pd.read_json('xp_data.json')
    df_poeng_expected = pd.merge(df_poeng, df_xp, on='Gameweek')
    return df_poeng_expected


def expected_poeng_c():
    df_poeng_c = pd.read_json('poeng_data_c.json', orient='records', lines=True)
    df_xp_c = pd.read_json('xp_data_c.json', orient='records', lines=True)
    df_poeng_expected_c = pd.merge(df_poeng_c, df_xp_c, on='Gameweek')
    return df_poeng_expected_c