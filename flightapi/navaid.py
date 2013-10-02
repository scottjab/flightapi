#!/usr/bin/python

class NavAid:
    navAidType = None
    freq = None
    navaidName = None
    navaidID = None
    lon = None
    lat = None
    def getCoords(self):
        return (self.lat,self.lon)