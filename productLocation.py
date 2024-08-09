class ProductLocation(object):
    def __init__(self, city, address, zip, quantity):
        self.city = city
        self.address = address
        self.zip = zip
        self.quantity = quantity
        self.distanceInFeet = None
        self.timeInSeconds = None