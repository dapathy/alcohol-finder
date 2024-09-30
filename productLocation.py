from typing import List


class ProductLocation(object):
    def __init__(self, city: str, address: str, zip: str, quantity: int, phoneNumber: str):
        self.city = city
        self.address = address
        self.zip = zip
        self.quantity = quantity
        self.phoneNumber = phoneNumber
        self.distanceInFeet = None
        self.timeInSeconds = None
        self.timeWithTrafficInSeconds = None

class Product(object):
    def __init__(self, itemCode: str, name: str, locations: List[ProductLocation]):
        self.itemCode = itemCode
        self.name = name
        self.locations = locations