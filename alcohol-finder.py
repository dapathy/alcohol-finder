import requests
from bs4 import BeautifulSoup
import googlemaps

from productLocation import ProductLocation

googleMapsApiKey = ""

def establishSession():
    url = "http://www.oregonliquorsearch.com"
    requestHeaders = {'Host': 'www.oregonliquorsearch.com'}
    response = requests.get(url, headers=requestHeaders, allow_redirects=True)
    return response.cookies["JSESSIONID"]

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

def queryProduct(sessionId, itemCode):
    url = f"http://www.oregonliquorsearch.com/product_details.jsp?productRowNum=1&rowCount=45&column=City&pageCurrent=1&pageCount=1&itemDisplay={itemCode}"
    cookies = {'JSESSIONID': sessionId}
    response = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    locations = []
    for row in soup.find_all(class_='alt-row'):
        city = row.select_one('td:nth-of-type(2)').text.strip()
        address = row.select_one('td:nth-of-type(3)').text.strip()
        zip = row.select_one('td:nth-of-type(4)').text.strip()
        quantity = row.select_one('td:nth-of-type(7)').text.strip()
        locations.append(ProductLocation(city, address, zip, quantity))
    return locations

itemCode = "99900607575"
sessionId = "bb3d2f2f1228dbb5655ee4c2b4b7"
origin = "229 S Seymour St, Portland, OR 97239"
# sessionId = establishSession()
locations = queryProduct(sessionId, itemCode)
distances = getDistanceMatrix(origin, locations)