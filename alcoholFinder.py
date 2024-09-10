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
    destinationAddresses = map(lambda x: f'{x.address}, {x.zip}', destinations) # consider including city

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    # Distance matrix has a limit of 25 destinations per request
    all_distances = []
    for batch in chunks(list(destinationAddresses), 25):
        matrix = mapsApi.distance_matrix(origin, list(batch), mode="driving", units="imperial", departure_time="now")
        distances = matrix["rows"][0]["elements"]
        all_distances.extend(distances)

    for i in range(len(all_distances)):
        if all_distances[i]["status"] == "OK":
            destinations[i].distanceInFeet = all_distances[i]["distance"]["value"]
            destinations[i].timeInSeconds = all_distances[i]["duration"]["value"]
            destinations[i].timeWithTrafficInSeconds = all_distances[i]["duration_in_traffic"]["value"]
        else:
            logging.warning(f"Distance matrix status: {all_distances[i]['status']} for {destinations[i].address}")

    sortedDistances = sorted(destinations, key=lambda x: (x.timeInSeconds is None, x.timeInSeconds))
    return sortedDistances

def queryProduct(itemCode):
    url = f"http://www.oregonliquorsearch.com/servlet/FrontController?radiusSearchParam=0&productSearchParam={itemCode}&locationSearchParam=portland&btnSearch=Search&view=global&action=search"
    response = session.get(url, allow_redirects=True)
    logging.info(f"Query response status code: {response.status_code}")

    # Increase page size
    url = f"http://www.oregonliquorsearch.com/servlet/FrontController?view=productdetails&action=pagechange&itemCode=6075B&newItemCode={itemCode}&productRowNum=1&column=City&pageSize=100"
    response = session.get(url, allow_redirects=True)
    logging.info(f"Page size response status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    locations = []
    for row in soup.find_all(class_=re.compile(r'\b(alt-row|row)\b')):
        quantity = row.select_one('td:nth-of-type(7)').text.strip()
        if (quantity == '0'):
            continue
        city = row.select_one('td:nth-of-type(2)').text.strip()
        address = row.select_one('td:nth-of-type(3)').text.strip()
        zip = row.select_one('td:nth-of-type(4)').text.strip()
        phoneNumber = row.select_one('td:nth-of-type(5)').text.strip()
        locations.append(ProductLocation(city, address, zip, quantity, phoneNumber))
    return locations