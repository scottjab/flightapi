#!/usr/bin/python
from navaid import NavAid

class RouteLeg:
    startNavaid = NavAid()
    endNavaid = NavAid()
    radial = None
    distance = None

    #Accesors
    def getDistance(self):
        """Returns the distance in nautical miles"""
        return self.distance
    def getDistanceInKM(self):
        """Returns the distance in kilometers"""
        return round(float(distance)*1.85200)

    def getRadial(self):
        """Returns the starting radial in degrees"""
        return radial

    def getStartCoords(self):
        """Returns a tuple with lat and long"""
        return (startNavaid.lat,startNavAid.lon)

    def getEndCoords(self):
        """Returns a tuple with lat and long"""
        return (endNavaid.lat, endNavaid.lon)
    #Mutators
    def setDistance(self,dist):
        self.distance = dist
    def setRadial(self,rad):
        self.radial = rad
    def setStartNavaid(self,startAid):
        self.startNavaid = startAid
    def setEndNavaid(self, endAid):
        self.endNavAid  = endAid

