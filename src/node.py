class Node:
    def __init__(self, iso3, average: float, country, data = None):
        self.iso3 = iso3
        self.average = average
        self.country = country
        self.data = data
        self.left = None
        self.right = None
        self.height = 0
        self.bFactor = 0
        self.pad = None

    def __str__(self):
        return self.iso3
