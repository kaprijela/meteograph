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

FILENAME = "temp-plot.html"

# Brno: 49.210722, 16.594185

# datetime format
FORMAT = "%Y-%m-%dT%XZ"

MAPS_URL = "https://maps.googleapis.com/maps/api/geocode/xml?address={}&key={}"
GEOCODING_API_KEY = "AIzaSyA4WbItbP-Gjde9H0v-e7uB8bK4vtkJkxM"

METEO_URL = "http://api.met.no/weatherapi/locationforecastlts/1.3/?lat={};lon={}"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and plot weather forecast for given location.")
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

    if PRINT_DEBUG:
        print()

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
    keys = []
    values = []

    for data in precipitation:
        if data["value"] != "0.0":
            keys.append(datetime.strptime(data.parent.parent["from"], FORMAT))
            values.append(data["value"])

        if PRINT_DEBUG:
            print(
                datetime.strptime(data.parent.parent["from"], FORMAT),
                datetime.strptime(data.parent.parent["to"], FORMAT),
                data["value"],
                sep='\t'
                )
    

    trace = go.Bar(
        x=keys,
        y=values,
        opacity=1,
        name="Precipitation",
        marker=dict(
            color="rgb(49,130,189)"
        )
    )

    trace_data.append(trace)
    


def plot_with_plotly(namespace, data, soup):
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

    fig = go.Figure(data=data, layout=layout)
    py.offline.plot(fig, filename=FILENAME)


if __name__ == "__main__":
    namespace = parse_arguments()
    
    if namespace.coordinates:
        setattr(namespace, "location", reverse_geocode(namespace, GEOCODING_API_KEY))
        
    else:
        setattr(namespace, "location", " ".join(namespace.address))
        setattr(namespace, "address", geocode("+".join(namespace.address), GEOCODING_API_KEY))

    soup = get_met_data(namespace)

    data = []
    get_temperatures(data, soup)
    get_precipitation(data, soup)

    if DRAW_PLOT:
        plot_with_plotly(namespace, data, soup)
