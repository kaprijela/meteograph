#!/usr/bin/env python3
"""
Meteograph

@author: Gabriela Kandova
Inspired by Klara weather app.
"""

# module imports
import argparse
from datetime import datetime

import plotly as py
import plotly.graph_objs as go

from bs4 import BeautifulSoup

import requests

# debug flags
PRINT_DEBUG = False
DRAW_PLOT = True

# 49.210722, 16.594185
# NAME = "Brno"

# datetime format
FORMAT = "%Y-%m-%dT%XZ"

MAPS_URL = "https://maps.googleapis.com/maps/api/geocode/xml?address={}&key={}"
GEOCODING_API_KEY = "AIzaSyA4WbItbP-Gjde9H0v-e7uB8bK4vtkJkxM"

METEO_URL = "http://api.met.no/weatherapi/locationforecastlts/1.3/?lat={};lon={}"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "address",
        nargs="+",
        help="address string for which to get weather forecast"
    )

    parser.add_argument(
        "-c", "--coordinates",
        action="store_true",
        default=False,
        help="use coordinates instead of an address"
    )

    return parser.parse_args()


def geocode(query, api_key):
    """
    Get latitude and longitude for given address.
    """
    response = requests.get(MAPS_URL.format(query, api_key))

    bsoup = BeautifulSoup(response.content, "html.parser")
    
    return [bsoup.find("lat").string, bsoup.find("lng").string]


def reverse_geocode(namespace, api_key):
    """
    Get address for given latitude and longitude.
    """
    response = requests.get(MAPS_URL.format(
        "{},{}".format(
            namespace.address[0], namespace.address[1]
            ), api_key)
        )

    bsoup = BeautifulSoup(response.content, "html.parser")
    return bsoup.find_all("address_component")[5].contents[1].string
    

def get_met_data(namespace):
    """
    Fetch meteodata from API.
    """
    url = METEO_URL.format(namespace.address[0], namespace.address[1])
    response = requests.get(url)

    bsoup = BeautifulSoup(response.content, "html.parser")

    return bsoup


def get_temperatures(trace_data, soup):
    """
    Searches the XML tree for (time, temperature) data.
    """

    if PRINT_DEBUG:
        print("\nTEMPERATURE\n")

    temperatures = soup.find_all("temperature")
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


def get_precipitation(trace_data, soup):
    """
    Searches the XML tree for (time, temperature) data.
    """

    precipitation = soup.find_all("precipitation")
    prec_list = []

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


def plot_with_plotly(namespace, soup):
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
        title="Weather for <b>{}</b> ({}, {})".format(namespace.location, namespace.address[0], namespace.address[1])
    )

    data = []

    get_temperatures(data, soup)
    get_precipitation(data, soup)

    if DRAW_PLOT:
        fig = go.Figure(data=data, layout=layout)
        py.offline.plot(fig, filename='temp-plot.html')


if __name__ == "__main__":
    namespace = parse_arguments()
    print(namespace)
    
    if namespace.coordinates:
        setattr(namespace, "location", reverse_geocode(namespace, GEOCODING_API_KEY))
        
    else:
        setattr(namespace, "location", " ".join(namespace.address))
        setattr(namespace, "address", geocode("+".join(namespace.address), GEOCODING_API_KEY))

    print(namespace)

    soup = get_met_data(namespace)
    plot_with_plotly(namespace, soup)
