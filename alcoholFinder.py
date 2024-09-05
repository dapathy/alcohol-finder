import os
import re
import requests
from bs4 import BeautifulSoup
import googlemaps
import logging

from productLocation import ProductLocation

googleMapsApiKey = os.environ['GOOGLE_MAPS_API_KEY']
session = requests.Session()

def establishSession():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'btnSubmit': "I'm 21 or older"}
    response = session.post("http://www.oregonliquorsearch.com/servlet/WelcomeController", allow_redirects=True, headers=headers, data=data)
    logging.info(f"Status code after age verification: {response.status_code}")

def getDistanceMatrix(origin, destinations):
    mapsApi = googlemaps.Client(key=googleMapsApiKey)
    destinationAddresses = map(lambda x: f'{x.address}, {x.zip}', destinations) # TODO: include city?
    matrix = mapsApi.distance_matrix(origin, list(destinationAddresses), mode="driving", units="imperial")
    distances = matrix["rows"][0]["elements"]

    for i in range(len(distances)):
        if distances[i]["status"] == "OK":
            destinations[i].distanceInFeet = distances[i]["distance"]["value"]
            destinations[i].timeInSeconds = distances[i]["duration"]["value"]

    sortedDistances = sorted(destinations, key=lambda x: (x.timeInSeconds is None, x.timeInSeconds))
    return sortedDistances

def queryProduct(itemCode):
    url = f"http://www.oregonliquorsearch.com/servlet/FrontController?radiusSearchParam=0&productSearchParam={itemCode}&locationSearchParam=portland&btnSearch=Search&view=global&action=search"
    # TODO: look into increasing page size
    response = session.get(url, allow_redirects=True)
    logging.info(f"Query response status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    locations = []
    for row in soup.find_all(class_=re.compile(r'\b(alt-row|row)\b')):
        city = row.select_one('td:nth-of-type(2)').text.strip()
        address = row.select_one('td:nth-of-type(3)').text.strip()
        zip = row.select_one('td:nth-of-type(4)').text.strip()
        quantity = row.select_one('td:nth-of-type(7)').text.strip()
        locations.append(ProductLocation(city, address, zip, quantity))
    return locations