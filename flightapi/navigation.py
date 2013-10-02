#!/usr/bin/env python
"""
Navigation.py

This code is a horror really needs review.

"""

from routeleg import RouteLeg
import math
import re
from navaid import NavAid
import numpy as np

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_

from navaidtables import *


class Navigation:
    engine = None

    def __init__(self, engine):
        # super(Navigation, self)
        self.engine = engine

    def decode_freq(self, encodedfreq):
        try:
            decodedFreq = str(hex(encodedfreq))[2:]
            decodedFreq = "%s.%s" % (decodedFreq[:3], decodedFreq[3:5])
            return decodedFreq
        except:
            return None

    def distance(self, origin, destination):
        try:
            lat1, lon1 = origin.getCoords()
            lat2, lon2 = destination.getCoords()
        except:
            lat1 = origin[0]
            lon1 = origin[1]
            lat2 = destination[0]
            lon2 = destination[1]

        radius = 6371  # km

        dlat2 = np.radians(lat2 - lat1)
        dlon2 = np.radians(lon2 - lon1)

        a2 = np.sin(np.divide(dlat2, 2.0)) * \
            np.sin(np.divide(dlat2, 2.0)) + \
            np.cos(np.radians(lat1)) * \
            np.cos(np.radians(lat2)) * \
            np.sin(np.divide(dlon2, 2)) * \
            np.sin(dlon2 / 2)

        c2 = np.multiply(2, np.arctan2(np.sqrt(a2),
                         np.sqrt(np.subtract(1, a2))))
        d2 = np.multiply(radius, c2)
        return d2

    def bearing(self, origin, destination):
        try:
            lat1, lon1 = origin.getCoords()
            lat2, lon2 = destination.getCoords()
        except:
            lat1 = origin[0]
            lon1 = origin[1]
            lat2 = destination[0]
            lon2 = destination[1]

        # dlat = math.radians(lat2 - lat1)
        dlon = math.radians(float(lon2) - float(lon1))
        y = math.sin(dlon) * math.cos(math.radians(lat2))

        x = math.cos(math.radians(lat1)) * \
            math.sin(math.radians(lat2)) - \
            math.sin(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * \
            math.cos(dlon)
        bearing = math.atan2(y, x)
        return (math.degrees(bearing) + 360) % 360

    def get_waypoint_distance(self, start, end):
        return self.distance((start['latitude'],
                              start['longtitude']),
                            (end['latitude'],
                             end['longtitude']))

    def get_waypoints_by_name(self, name):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # sql = '''select id,ident,collocated,name,latitude,longtitude,NavaidId
        # from waypoints where ident = '%s' ''' % name
        query = session.query(Waypoint).filter(Waypoint.ident == name)
        waypoints = []

        for waypoint in query:
            # converting to dictionary for now, will fix later.
            waypoint = {}
            waypoint['id'] = waypoint.id
            waypoint['ident'] = waypoint.ident
            waypoint['collocated'] = waypoint.collocated
            waypoint['name'] = waypoint.name
            waypoint['latitude'] = waypoint.latitude
            waypoint['longtitude'] = waypoint.longtitude
            waypoint['navaidId'] = waypoint.navaidId
            waypoint['navaid'] = waypoint.navaid
            waypoints.append(waypoint)
        session.close()
        return waypoints

    def get_waypoint_by_id(self, id):
        # sql = '''select id,ident,collocated,name,latitude,longtitude,NavaidId
        # from waypoints where id = %i ''' % id
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Waypoint).filter(Waypoint.id == id)
        for waypoint in query:
            # converting to dictionary for now, will fix later.
            waypoint = {}
            waypoint['id'] = waypoint.id
            waypoint['ident'] = waypoint.ident
            waypoint['collocated'] = waypoint.collocated
            waypoint['name'] = waypoint.name
            waypoint['latitude'] = waypoint.latitude
            waypoint['longtitude'] = waypoint.longtitude
            waypoint['navaidId'] = waypoint.navaidId
            waypoint['navaid'] = waypoint.navaid
            session.close()
            return waypoint

    def remove_duplicate_waypoint(self, route):
            # hack to fix the fact that all loops are for eaches in python.
        fixedRoute = []
        for x in xrange(len(route)):
            if x > 0:
                if route[x] != route[x - 1]:
                    fixedRoute.append(route[x])
            else:
                fixedRoute.append(route[x])
        return fixedRoute

    def tokenizer(self, route):
        splitroute = re.split('[ .]', route)
        return splitroute

    def parser(self, route):
        tokens = self.tokenizer(route)
        # print tokens
        depAirport = tokens.pop(0)
        arrAirport = tokens.pop()
        procedure = re.compile(r'.[0-9]', re.IGNORECASE)
        flownRoute = []
        flownRoute.append(depAirport)
        # print len(tokens)
        for x in xrange(len(tokens)):
            if len(procedure.findall(tokens[x])) > 0:
                if x == 0:
                    terminal = self.get_terminal(depAirport,
                                                 tokens[x],
                                                 tokens[x + 1])
                    flownRoute.extend(terminal)
                    # print "%i: FOUND SID: %s Transition: %s FIXES %s" %
                    # (x,tokens[x],tokens[x+1], " ".join(terminal))
                elif x == len(tokens) - 1:
                    terminal = self.get_terminal(arrAirport,
                                                 tokens[x],
                                                 tokens[x - 1])
                    flownRoute.extend(terminal)
                    # print "%i: FOUND STAR: %s Transition: %s FIXES %s "  %
                    # (x,tokens[x],tokens[x-1]," ".join(terminal))
                else:
                    airway = self.get_airway(tokens[x - 1],
                                             tokens[x],
                                             tokens[x + 1])
                    flownRoute.extend(airway)
                    # print "%i: FOUND AIRWAY: %s AIRWAY FIXES: %s " %
                    # (x,tokens[x], " ".join(airway))
            else:
                flownRoute.append(tokens[x])
                # print "%i: %s" % (x,tokens[x])
        flownRoute.append(arrAirport)
        return self.remove_duplicate_waypoint(flownRoute)

    def get_airway(self, entry, airway, exit):

        # I am dumb.
        Session = sessionmaker(bind=self.engine)
        session = Session()

        airways = []

        waypoint1_alias = aliased(Waypoint)
        waypoint2_alias = aliased(Waypoint)
        query = (
            session.query(Airway, waypoint1_alias.ident.label('wp1_ident'),
                          waypoint1_alias.id.label('wp1_id'),
                          waypoint2_alias.ident.label('wp2_ident'),
                          waypoint2_alias.id.label('wp2_id'),
                          AirwayLeg.isStart,
                          AirwayLeg.isEnd)
            .outerjoin(AirwayLeg, AirwayLeg.airwayID == Airway.id)
            .join(waypoint1_alias, AirwayLeg.waypoint1ID == waypoint1_alias.id)
            .join(waypoint2_alias, AirwayLeg.waypoint2ID == waypoint2_alias.id)
            .filter(Airway.ident == airway))

        for row in query:
            if row.isStart == 1:
                airways.append(row.wp1_ident)
            elif row.isEnd == 1:
                airways.append(row.wp2_ident)
            else:
                airways.append(row.wp2_ident)
        try:
            entryPos = airways.index(entry)
            exitPos = airways.index(exit)
            if entryPos < exitPos:
                return airways[entryPos:exitPos + 1]
            else:
                return airways[exitPos:entryPos]
        except ValueError:
            pass
        session.close()

    def get_airwayRoute(self, airwayid, current, next, end, route):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        #                 0      1     2      3          4           5       6
        # sql = '''select id,airwayid,level,waypoint1id,waypoint2id,isstart,isend from airwaylegs where airwayid = %s and waypoint1id = %s  and waypoint2id <> %s''' % (airwayid, next, current)
        # print "get_airway: " + sql
        # c.execute(sql)
        res = session.query(AirwayLeg).filter(AirwayLeg.id == airwayid,
                                              AirwayLeg.waypoint1ID == next,
                                              AirwayLeg.waypoint2ID != current)
        for al in res:
            # print row
            for waypoint in end:
                print "WAYPOINTS: %s == %s " % (waypoint['id'], al.waypoint2ID)
                if waypoint['id'] == al.waypoint2ID:
                    session.close()
                    return " " + self.get_waypoint_by_id(al.waypoint1ID)['ident'] + " " + waypoint['ident']
                    # TODO: FIX THIS
                    # route.append(self.get_waypoint_by_id(al.waypoint1ID)
                    # route.append(waypoint)
                    # return route
            if al.isEnd > al.isStart:
                return None
            print route
            route.append(self.get_waypoint_by_id(al.waypoint1ID))
            session.close()
            return self.get_airwayRoute(airwayid, al.waypoint1ID, al.waypoint2ID, end, route)

    def get_terminal(self, airport, name, transition):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # conn = self.conn
        # c = self.c
        # terminalLegsSQL = '''select id,wptid from terminallegs where  Transition = '%s' and terminalid in (select id from terminals where ICAO = '%s' and fullname = '%s')'''
        # waypointSQL = '''select ident,Latitude,Longtitude from waypoints where id = %i'''
        # c.execute(terminalLegsSQL % (transition, airport, name))

        res = session.query("id", "wptid").from_statement("select id,wptid from terminallegs where  Transition = :transition and terminalid in (select id from terminals where ICAO = :airport and fullname = :name").params(
            transition=transition, airport=airport, name=name)

        waypointidlist = []
        for row in res:
            waypointidlist.append(row[1])
        waypoints = []
        for waypointID in waypointidlist:
            res = session.query(Waypoint).filter(Waypoint.id == waypointID)
            for way in res:
                waypoints.append(way.ident)
        session.close()
        return waypoints

    def get_navaid_by_id(self, idName, lastNavaid):
        """Returns the Closest NavAid with the ID Given,
           if no last Navaid is given it will return the first row"""
        # holy crap do I need to rewrite this
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query("Ident", "Latitude", "Longtitude", "Name", "Navaidid").from_statement(
            "SELECT ICAO AS Ident, Latitude, Longtitude, Name, primaryid AS Navaidid FROM Airports WHERE ICAO = :ident UNION ALL SELECT Ident, Latitude, Longtitude, Name, Navaidid FROM Waypoints WHERE Ident = :ident").params(ident=idName)

        navaid = NavAid()
        smallAid = None

        for row in res:
            currentNavaid = NavAid()
            currentNavaid.navaidID = row.Ident
            currentNavaid.lat = row.Latitude
            currentNavaid.lon = row.Longtitude
            currentNavaid.comment = row.Name

            # I don't know why this was setting this before, probably legacy
            # -mattk
            if row.Navaidid is not None:
                freqResult = session.query(Navaid).filter(
                    Navaid.ident == row.Ident).first()
                freq = int(freqResult.freq)
                currentNavaid.freq = self.decode_freq(freq)
            if lastNavaid is not None:
                tempDistance = self.distance(lastNavaid, currentNavaid)
                if smallAid is None:
                    smallLeg = tempDistance
                    navaid = currentNavaid
                    currerentNavaid = None
                elif smallAid > tempDistance:
                    navaid = currentNavaid
                    currentNavaid = None
            else:
                navaid = currentNavaid
                currentNavaid = None

        session.close()
        return navaid

    def calculate_route(self, route):
        """Accepts routes as a tuple and returns an tuple of RouteLegs"""
        calculatedRoute = []
        # need to make this NOT JAVAY
        for i in range(len(route) - 1):
            leg = RouteLeg()
            leg.startNavaid = self.get_navaid_by_id(
                idName=route[i], lastNavaid=None)
            leg.endNavaid = self.get_navaid_by_id(
                idName=route[i + 1], lastNavaid=leg.startNavaid)
            leg.distance = np.multiply(self.distance(
                leg.startNavaid, leg.endNavaid), 0.539956803)
            leg.radial = int(self.bearing(leg.startNavaid, leg.endNavaid))
            calculatedRoute.append(leg)
        return calculatedRoute

    def calculate_time(self, speed, total):
        time = total / float(speed) * 60 * 60
        print int(round(total, 0))
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        print "%d:%02d:%02d" % (h, m, s)

    def find_reciprocal(self, runway):
        runwayHeading = 0
        runwayPosition = None
        reciprocalPosition = None
        reciprocalHeading = None

        if len(runway) > 2:
            runwayPosition = str(list(runway)[2])
            runwayHeading = int(runway[:-1])
        else:
            runwayHeading = int(runway)
        if runwayHeading <= 18:
            reciprocalHeading = runwayHeading + 18
        else:
            reciprocalHeading = runwayHeading - 18

        if runwayPosition is not None:
            if runwayPosition == 'R':
                reciprocalPosition = 'L'
            elif runwayPosition == 'L':
                reciprocalPosition = 'R'
            else:
                reciprocalPosition = 'C'
        if reciprocalPosition is not None:
            return str(reciprocalHeading) + reciprocalPosition
        else:
            return str(reciprocalHeading)

    def get_navaid_info(self, ident):
        """Returns navaid info to bot"""
        ident = str(ident).upper()
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # conn = self.conn
        # c = self.c
        # navaidSQLTemplate = """select * from v_navaids where ident = '%s'"""
        res = session.query("ident", "name", "freq", "DESC", "country").from_statement(
            "select * from v_navaids where ident = :ident").params(ident=ident)
        # navaidSQL = navaidSQLTemplate % ident
        # c.execute(navaidSQL)
        results = []
        morseAlphabet = {
            "A": ".-",
            "B": "-...",
            "C": "-.-.",
            "D": "-..",
            "E": ".",
            "F": "..-.",
            "G": "--.",
            "H": "....",
            "I": "..",
            "J": ".---",
            "K": "-.-",
            "L": ".-..",
            "M": "--",
            "N": "-.",
            "O": "---",
            "P": ".--.",
            "Q": "--.-",
            "R": ".-.",
            "S": "...",
            "T": "-",
            "U": "..-",
            "V": "...-",
            "W": ".--",
            "X": "-..-",
            "Y": "-.--",
            "Z": "--..",
            " ": "/"
        }
        for row in res:
            result = {}
            result['ident'] = row[0]
            morse = ""
            for char in result['ident'][:]:
                morse += morseAlphabet[char.upper()] + " "
            result['morse'] = morse
            result['name'] = row[1]
            encodedFreq = row[2]
            decodedFreq = str(hex(row[2]))[2:]
            decodedFreq = "%s.%s" % (decodedFreq[:3], decodedFreq[3:5])
            result['freq'] = decodedFreq
            result['desc'] = row[3]
            result['country'] = row[4]
            if 'K' in result['country']:
                results.insert(0, result)
            else:
                results.append(result)
        if len(results) > 0:
            session.close()
            return results
        else:
            session.close()
            return None

    def get_airport_info(self, icao):
        """Grab info about a field for the bot"""
        icao = str(icao).upper()
        Session = sessionmaker(bind=self.engine)
        session = Session()

        resultSet = {}
        airportId = None
        elevation = 0
        name = ""
        # airportSql = """select id,name,elevation from airports where ICAO like '%%%s' """ % icao
        # print airportSql
        # c.execute(airportSql)
        try:
            ap = session.query(Airport).filter(
                Airport.icao.like('%%%s' % icao)).one()
        except:
            return resultSet
        airportId = ap.id
        resultSet['name'] = ap.name
        resultSet['elevation'] = ap.elevation
        runways = []
        # c.execute("""select ident, length, TrueHeading, Surface, Elevation
        # from runways where AirportID = %i order by ident""" % int(airportId))

        for runway in ap.runways:
            ident = runway.ident
            length = runway.length
            if len(ident) > 2:
                runwayHeading = int(ident[:-1])
            else:
                runwayHeading = int(ident)
            if runwayHeading <= 18:
                rw = {}
                rw['ident'] = ident + "/" + self.find_reciprocal(ident)
                rw['length'] = runway.length
                rw['heading'] = runway.trueHeading
                rw['surface'] = runway.surfaceType.description
                rw['elevation'] = runway.elevation
                runways.append(rw)
        resultSet['runways'] = runways
        session.close()
        return resultSet

    def get_ils(self, airportICAO=None, runwayIdent=None):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        if airportICAO is None:
            return "Need an airport and a runway."
        if runwayIdent is None:
            for airport in session.query(Airport).filter(Airport.icao == airportICAO):
                runwayList = []
                for runway in airport.runways:
                    ils = runway.ils
                    if len(ils) > 0:
                        runwayList.append(runway.ident)
                if len(runwayList) > 0:
                    session.close()
                    return "%s: ILS on the following runways: %s " % (airport.icao, ", ".join(runwayList))
                else:
                    session.close()
                    return "%s does not have any ILSes available" % airport.icao
        else:
            for airport in session.query(Airport).filter(Airport.icao == airportICAO):
                responses = []
                for runway in session.query(Runway).filter(and_(Runway.airportID == airport.id, Runway.ident == runwayIdent)):
                    if len(runway.ils) < 1:
                        session.close()
                        return "%s does not have an ILS." % runwayIdent
                    for ils in runway.ils:
                        responses.append("%s: Freq: %s  Course: %s  ident: %s" % (
                            runwayIdent, self.decode_freq(ils.freq), ils.locCourse, ils.ident))
                if len(responses) == 0:
                    session.close()
                    return "%s is not a vaild runway at %s." % (runwayIdent, airportICAO)
                session.close()
                return "%s: %s" % (airportICAO, "; ".join(responses))
