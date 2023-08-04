import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import openpyxl



import xp
from xp import *
def transfer_in(data, gameweek):
   transferin = data.loc[(data["week"]==gameweek) & (data['transfer_in']== 1), ["name","team"]]
   return [f"{x[0]} ({x[1]})" for x in transferin.values]

def transfer_out(data, gameweek):
   transferout = data.loc[(data["week"]==gameweek) & (data['transfer_out']== 1), ["name","team"]]
   return [f"{x[0]} ({x[1]})" for x in transferout.values]

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

    return int((expected_points.sum() + doubled_captain.sum()).iloc[0])