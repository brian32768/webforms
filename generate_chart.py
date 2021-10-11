#!/usr/bin/env -S conda run -n covid python
#
#   Creates an HTML file containing the "daily cases" chart.
#
#   You should be able to generate a new chart any old time
#   by running this from the command line. 
#
#   Just do the following from a command prompt
# 
#      ./generate_chart.py my_chart.html
#
#   Then copy my_chart.html to the right place,
#
#      cp my_chart.html ~/docker/capacity/html/cases/index.html
#
import os, sys
import pandas as pd
import numpy as np
import arcgis.gis as GIS
import arcgis.features as Features
from datetime import datetime
import read_cases
import plotly.graph_objects as go


def generate_chart(sdf):
    # https://github.com/d3/d3-3.x-api-reference/blob/master/Formatting.md#d3_format
    cases = go.Bar(x=daily['date'], y=daily['cases'], name="Cases/day", marker_color="#f09665", hoverinfo="all")
    avg   = go.Scatter(x=daily['date'], y=daily['avg'], name="7 day avg", marker_color="#671d85")
    fig = go.Figure(data=[cases,avg])
    fig.update_xaxes(dtick="M1", tickformat="%b")
    fig.update_traces(hovertemplate="%{x|%b %d}: <b>%{y} cases</b>", selector=dict(type='bar'))
    fig.update_traces(hovertemplate="%{x|%b %d}: %{y:.1f} avg", selector=dict(type='scatter'))

    timestamp = datetime.now().strftime("<i>updated %b %d %H:%M</i>")
    fig.update_layout(title="<b>Clatsop County Daily Coronavirus Cases</b><br /> %s" % timestamp)

    return fig

if __name__ == '__main__':

    sdf = read_cases.read_daily_cases_df()
    print(sdf)

    sdf = read_cases.read_local_cases_df()
    (daily, total) = read_cases.clean_data(sdf, days = 30*4)

    fig = generate_chart(sdf)
    
    try:
        fig.write_html(sys.argv[1])
    except IndexError:
        print("Give me a filename if you want HTML output.")
        fig.show()
