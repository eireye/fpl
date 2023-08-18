import plotly.graph_objs as go
import plotly.offline as pyo

import xp
from xp import *


import plotly.graph_objs as go
import plotly.offline as pyo

def poeng_vs_expected_graf(data):
    # Calculate the mean of the "poeng" column
    poeng_mean = data[data["Points"] != 0]["Points"].mean()
    
    # Calculate the mean of the "xp" column, excluding zero values
    xp_mean = data[data["XP"] != 0]["XP"].mean()
    
    # Create a line plot using Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=data["Gameweek"], y=data["Points"], mode="lines+markers", name="Faktisk poeng"))
    fig.add_trace(go.Scatter(x=data[data["XP"] != 0]["Gameweek"], y=data[data["XP"] != 0]["XP"], mode="lines+markers", name="Forventet poeng"))
    fig.add_shape(type="line", x0=data["Gameweek"].min(), y0=poeng_mean, x1=data["Gameweek"].max(), y1=poeng_mean, line=dict(color="blue", width=5, dash="dot"), name="Gjennomsnitt faktisk poeng")
    fig.add_shape(type="line", x0=data["Gameweek"].min(), y0=xp_mean, x1=data["Gameweek"].max(), y1=xp_mean, line=dict(color="red", width=5, dash="dot"), name="Gjennomsnitt forventet poeng")
    
    fig.add_annotation(x=data["Gameweek"].max(), y=poeng_mean, text=f"Gjennomsnitt faktisk poeng: {poeng_mean:.2f}", showarrow=False, font=dict(size=12, color="black"), yshift=10)
    fig.add_annotation(x=data["Gameweek"].max(), y=xp_mean, text=f"Gjennomsnitt forventet poeng: {xp_mean:.2f}", showarrow=False, font=dict(size=12, color="black"), yshift=10)
    fig.update_layout(
        title=f"Expected poeng vs Faktiske poeng",
        xaxis_title="Gameweek",
        yaxis_title="poeng",
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

        height=600,
        
        
        font=dict(size=16)
        ,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    
    # Generate the HTML code for the plot
    plot_html = pyo.plot(fig, output_type='div')
    
    # Return the HTML code as a string
    return plot_html

