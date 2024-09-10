class ProductLocation(object):
    def __init__(self, city, address, zip, quantity, phoneNumber):
        self.city = city
        self.address = address
        self.zip = zip
        self.quantity = quantity
        self.phoneNumber = phoneNumber
        self.distanceInFeet = None
        self.timeInSeconds = None