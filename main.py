"""
Get Your Own Damn Weather™

@author: Gabriela Kandova
Inspired by Klara weather app.
"""

# module imports
from datetime import datetime

import plotly as py
import plotly.graph_objs as go

from bs4 import BeautifulSoup

import requests

# 49.210722, 16.594185
LOCATION = "Brno"
LATITUDE = "49.210722"
LONGITUDE = "16.594185"
URL = "http://api.met.no/weatherapi/locationforecastlts/1.3/?lat={};lon={}".format(
    LATITUDE, LONGITUDE
    )

FORMAT = "%Y-%m-%dT%XZ"

# debug flags
PRINT_DEBUG = False
SOUP_DEBUG = False
DRAW_PLOT = True


def get_met_data():
    """
    Fetch meteodata from API
    """
    response = requests.get(URL)

    if SOUP_DEBUG:
        with open("soup.html", "w") as file:
            file.write(response.text)

    return response


def parse_response(response):
    """
    Parse resulting XML
    """
    bsoup = BeautifulSoup(response.content, "html.parser")

    return bsoup


def get_temperatures(trace_data):
    """
    Searches the XML tree for (time, temperature) data.
    """

    if PRINT_DEBUG:
        print("\nTEMPERATURE\n")

    temperatures = SOUP.find_all("temperature")
    x = list()
    y = list()
    for data in temperatures:
        x.append(datetime.strptime(data.parent.parent["from"], FORMAT))
        y.append(data["value"])

        if PRINT_DEBUG:
            print(
                datetime.strptime(data.parent.parent["from"], FORMAT),
                datetime.strptime(data.parent.parent["to"], FORMAT),
                data["value"],
                sep='\t'
                )

    trace = go.Scatter(
        x=x,
        y=y,
        fill="tozeroy",
        name="Temperature",
        line=dict(shape="spline", color="orange")
    )

    trace_data.append(trace)


def get_precipitation(trace_data):
    """
    Searches the XML tree for (time, temperature) data.
    """

    precipitation = SOUP.find_all("precipitation")
    prec_list = []

    # x = list()
    # y = list()

    if PRINT_DEBUG:
        print("\nPRECIPITATION\n")

    for data in precipitation:
        prec_list.append(
            (
                datetime.strptime(data.parent.parent["from"], FORMAT),
                datetime.strptime(data.parent.parent["to"], FORMAT),
                data["value"]
            )
        )

        # x.append(datetime.strptime(data.parent.parent["from"], FORMAT))
        # y.append(data["value"])
        """
        if PRINT_DEBUG:

            print(
                datetime.strptime(data.parent.parent["from"], FORMAT),
                datetime.strptime(data.parent.parent["to"], FORMAT),
                data["value"],
                sep='\t'
                )
        """
    # TODO: sort list of tuples

    trace = go.Bar(
        x=[time[0] for time in prec_list],
        y=[value[2] for value in prec_list],
        opacity=1,
        name="Precipitation",
        marker=dict(
            color="rgb(49,130,189)"
        )
    )

    trace_data.append(trace)


def partition_into_days(result):
    """
    Partition data into days, unused atm
    """

    days = [[]]
    index = 0

    # do this more efficiently
    for time in result[0]:
        if str(time)[11:] == "00:00:00" and days[index] != []:
            days.append(list())
            index += 1

        days[index].append(time)

    return days


def plot_with_plotly():
    """
    Plot temperature and precipitation data with plotly
    """
    layout = go.Layout(
        xaxis=dict(
            gridcolor="#dbdbdb",
            gridwidth=2,
            type="date"
        ),
        yaxis=dict(
            title="Temperature in °C"
        ),
        title="Weather in <b>{}</b> ({}, {})".format(LOCATION, LATITUDE, LONGITUDE)
    )

    data = []

    get_temperatures(data)
    get_precipitation(data)

    if DRAW_PLOT:
        fig = go.Figure(data=data, layout=layout)
        py.offline.plot(fig, filename='temp-plot.html')


if __name__ == "__main__":
    SOUP = parse_response(get_met_data())

    plot_with_plotly()
