import uuid
from math import radians, cos, sin, asin, sqrt
import requests
import urllib.parse
from pprint import pprint
import networkx as nx
import matplotlib.pyplot as plt


class Address:
    
    def __init__(self, name, lat, lon, full_address) -> None:
        self.id = uuid.uuid4()
        self.name = name
        self.full_address = full_address
        self.lat = lat
        self.lon = lon

        self.connexion = {}

    def calcDistance(self, point):
        lon1 = radians(self.lon)
        lat1 = radians(self.lat)

        lon2 = radians(point.lon)
        lat2 = radians(point.lat)
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    
        c = 2 * asin(sqrt(a))
        r = 6371
        dist = c * r

        self.connexion[point.id] = dist
        point.connexion[self.id] = dist

        return dist

    def to_json(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "full_address" : self.full_address,
            "lat" : self.lat,
            "lon" : self.lon
        }

class Session:
    def __init__(self, token) -> None:
        self.token = token

        self.address = []
        self.graph = []

    def addAddressWithData(self, name, lat, lon):
        self.address.append(Address(name, lat, lon))

    def addAddress(self, address):
        self.address.append(address)

    def calcAllDistances(self):
        for address in self.address:

            for second_address in self.address:

                if address.id == second_address.id:
                    break

                if second_address.id in address.connexion:
                    break

                address.calcDistance(second_address)

    def getAddressWithId(self, uuid):
        try:
            return [add for add in self.address if add.id == uuid][0]
        except:
            return None

    def getAddressWithTitle(self, name):
        try:
            return [add for add in self.address if add.name == name][0]
        except:
            return None

    def drawGraph(self, start_address_id=0):
        add = self.address[start_address_id]
        visited = [add]

        while True:
            res = sorted(add.connexion.items(), key=lambda x: x[1])
            
            flag = True
            for item in res:

                item = self.getPointWithId(item[0])

                if item not in visited:
                    add = item
                    visited.append(add)
                    flag = False

                    break
            if flag:
                break
        
        self.graph = visited

        return visited

    def genVisualisation(self):
        if(self.graph != []):
            
            labels = [x.name for x in self.graph]
            x = [i for i in range(0, len(self.graph) * 2, 2)]
            y = [1 for i in range(len(x))]

            fig, ax = plt.subplots(1, 1, figsize=(15, 7))
            
            ax.plot(x, y, color="#83BCFF")
            ax.scatter(x, y, color="#83BCFF", s=[1000 for i in range(len(x))], alpha=1)
            
            for id_, label in enumerate(labels):
                ax.text(
                    x[id_]-0.005, 
                    y[id_]+0.006, 
                    s=label,
                    color="#FFFFFF"
                )
            
            ax.axis("off")            
            ax.set_facecolor("#0e1117")
            fig.set_facecolor("#0e1117")

            fig.savefig(self.token + ".png")

    def build(self):
        if len(self.address) >= 1:
            self.calcAllDistances()
            self.drawGraph()
            self.genVisualisation()

            return True

        else:
            return False
        
    def to_json(self):
        return {
            "token" : self.token,
            "address" : [address.to_json for address in self.address]
        }

def getPointWithLabel(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

    response = requests.get(url).json()

    if(response == []):
        return None

    full_address = response[0]["display_name"]
    name = full_address.split(",")[0]
    lat = float(response[0]["lat"])
    lon = float(response[0]["lon"])

    return Address(name, lat, lon, full_address)
            

if __name__ == "__main__":
    g = Session("a")

    address2 = 'Notre Dame Paris'
    p2 = getPointWithLabel(address2)    
    g.addAddress(p2)

    address3 = "Sébastopol Paris"
    p3 = getPointWithLabel(address3)    
    g.addAddress(p3)

    address4 = "Panthéon Paris"
    p4 = getPointWithLabel(address4)    
    g.addAddress(p4)

    address5 = "Pont Alexandre Paris"
    p5 = getPointWithLabel(address5)    
    g.addAddress(p5)

    g.build()