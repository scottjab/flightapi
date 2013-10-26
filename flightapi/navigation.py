#!/usr/bin/env python
"""
Navigation.py

This code is a horror really needs review.

"""

import math
import re
import numpy as np

from sqlalchemy.orm import sessionmaker, aliased

from navaidtables import *


class Navigation:
    engine = None

    def __init__(self, engine):
        # super(Navigation, self)
        self.engine = engine

    def session_builder(self, session):
        if session is None:
            Session = sessionmaker(bind=self.engine)
            session = Session()
        return session

    def close_session(self, existing_session, session):
        if existing_session is None:
            session.close()

    def decode_freq(self, encodedfreq):
        try:
            decodedFreq = str(hex(encodedfreq))[2:]
            decodedFreq = "%s.%s" % (decodedFreq[:3], decodedFreq[3:5])
            return decodedFreq
        except:
            return None

    def distance(self, origin, destination):
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

    def get_waypoint(self, ident, next_waypoint=None, existing_session=None):
        session = self.session_builder(existing_session)
        query = None
        try:
            ident = int(ident)
            query = session.query(Waypoint).filter(Waypoint.id == ident)
        except (ValueError, TypeError):
            query = session.query(Waypoint).filter(Waypoint.ident == ident)
        waypoints = []

        for waypoint_row in query:
            waypoint = {}
            if waypoint_row.navaid is not None:
                navaid = waypoint_row.navaid
                waypoint['freq'] = self.decode_freq(navaid.freq)
                waypoint['morse'] = self.morse_code(waypoint_row.ident)
                waypoint['channel'] = navaid.channel
                waypoint['usage'] = navaid.usage
                waypoint['elevation'] = navaid.elevation
                waypoint['slavedVar'] = navaid.slavedVar
                waypoint['name'] = navaid.name
            waypoint['ident'] = waypoint_row.ident
            waypoint['latitude'] = waypoint_row.latitude
            waypoint['longtitude'] = waypoint_row.longtitude
            waypoint['collocated'] = waypoint_row.collocated
            waypoints.append(waypoint)

        # logic to figure out which waypoint you really want.
        if next_waypoint is not None and not isinstance(ident, int):
            next_waypoints = None
            if isinstance(next_waypoint, str):
                next_waypoints = self.get_waypoint(next_waypoint,
                                                   existing_session=session)
            elif isinstance(next_waypoint, dict):
                next_waypoints = [next_waypoint]
            if next_waypoints is not None:
                current_shortest = None
                shortest_waypoint = None
                for waypoint in waypoints:
                    for next_point in next_waypoints:
                        distance = self.get_waypoint_distance(waypoint,
                                                              next_point)
                        if current_shortest is None:
                            current_shortest = distance
                            shortest_waypoint = waypoint
                        elif distance < current_shortest:
                            shortest_waypoint = waypoint
                    self.close_session(existing_session, session)
                return [shortest_waypoint]
        self.close_session(existing_session, session)
        if len(waypoints) > 0:
            return waypoints
        return None

    def get_waypoint_distance(self, start, end):
        return self.distance((start['latitude'],
                              start['longtitude']),
                            (end['latitude'],
                             end['longtitude']))

    def remove_duplicate_waypoint(self, route):
        result = []
        last = None
        for waypoint in route:
            if last is not None:
                if not waypoint['ident'] == last:
                    result.append(waypoint)
            else:
                result.append(waypoint)
            last = waypoint['ident']
        return result

    def tokenizer(self, route):
        splitroute = re.split('[ .]', route)
        return splitroute

    def parser(self, route):
        tokens = self.tokenizer(route)
        depAirport = tokens.pop(0)
        arrAirport = tokens.pop()
        procedure = re.compile(r'.[0-9]', re.IGNORECASE)
        flownRoute = []
        flownRoute.append(self.get_airport(depAirport))
        for x in xrange(len(tokens)):
            if len(procedure.findall(tokens[x])) > 0:
                if x == 0:
                    terminal = self.get_terminal(depAirport,
                                                 tokens[x],
                                                 tokens[x + 1])
                    flownRoute.extend(terminal)
                elif x == len(tokens) - 1:
                    terminal = self.get_terminal(arrAirport,
                                                 tokens[x],
                                                 tokens[x - 1])
                    flownRoute.extend(terminal)
                else:
                    airway = self.get_airway(tokens[x - 1],
                                             tokens[x],
                                             tokens[x + 1])
                    flownRoute.extend(airway)
            else:
                if x < len(tokens) - 1:
                    flownRoute.append(self.get_waypoint(tokens[x],
                                      next_waypoint=tokens[x + 1])[0])
                elif x == len(tokens) - 1:
                    flownRoute.append(self.get_waypoint(tokens[x],
                                      next_waypoint=tokens[x - 1])[0])
        flownRoute.append(self.get_airport(arrAirport))
        flownRoute = self.remove_duplicate_waypoint(flownRoute)
        result = {}
        result['filed_route'] = route
        result['flown_route'] = " ".join(
            [waypoint['ident'] for waypoint in flownRoute])
        result['expanded_route'] = flownRoute
        return result

    def get_airway(self, entry, airway, exit, existing_session=None):
        # I am dumb.
        session = self.session_builder(existing_session)
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
        rows = session.execute(query)
        airway_ids = []
        for row in rows.fetchall():
            if row[6] == 1:
                airway_ids.append(row[3])
            else:
                airway_ids.append(row[5])

        for waypoint in airway_ids:
            airways.append(self.get_waypoint(int(waypoint),
                                             existing_session=session)[0])
        self.close_session(existing_session, session)
        try:
            entryPos = -1
            exitPos = -1
            for i, waypoint in enumerate(airways):
                if waypoint['ident'] == entry:
                    entryPos = i
                elif waypoint['ident'] == exit:
                    exitPos = i
                elif entryPos > -1 and exitPos > -1:
                    break
            if entryPos < exitPos:
                return airways[entryPos:exitPos + 1]
            else:
                return airways[exitPos:entryPos]
        except ValueError:
            pass
        return None

    def get_terminal(self, airport, name, transition, existing_session=None):
        session = self.session_builder(existing_session)
        query_template = """SELECT ID,WptID FROM TerminalLegs
        WHERE Transition = :transition AND TerminalID
        IN (select ID FROM Terminals
        WHERE ICAO = :airport AND FullName = :name)"""
        res = session.query("ID", "WptID").from_statement(query_template).params(transition=transition, airport=airport, name=name)
        waypoints = []
        for row in res:
            waypoints.append(self.get_waypoint(row[1])[0])
        self.close_session(existing_session, session)
        return waypoints

    def calculate_time(self, speed, total):
        time = total / float(speed) * 60 * 60
        print int(round(total, 0))
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        print "%d:%02d:%02d" % (h, m, s)

    def get_airport(self, icao, existing_session=None):
        """Grab info about a field for the bot"""
        icao = str(icao).upper()
        session = self.session_builder(existing_session)
        resultSet = {}
        try:
            ap = session.query(Airport).filter(
                Airport.icao.like('%%%s' % icao)).one()
        except:
            return resultSet
        resultSet['ident'] = ap.icao
        resultSet['name'] = ap.name
        resultSet['elevation'] = ap.elevation
        resultSet['latitude'] = ap.latitude
        resultSet['longtitude'] = ap.longtitude
        runways = []
        # c.execute("""select ident, length, TrueHeading, Surface, Elevation
        # from runways where AirportID = %i order by ident""" % int(airportId))

        for runway in ap.runways:
            rw = {}
            rw['ident'] = runway.ident
            rw['length'] = runway.length
            rw['heading'] = runway.trueHeading
            rw['surface'] = runway.surfaceType.description
            rw['elevation'] = runway.elevation
            rw['latitude'] = runway.latitude
            rw['longtitude'] = runway.longtitude
            rw['width'] = runway.width
            if len(runway.ils) > 0:
                ilsobj = runway.ils[0]
                ils = {}
                ils['freq'] = self.decode_freq(ilsobj.freq)
                ils['gs_angle'] = ilsobj.gsAngle
                ils['latitude'] = ilsobj.latitude
                ils['longtitude'] = ilsobj.longtitude
                ils['category'] = ilsobj.category
                ils['ident'] = ilsobj.ident
                ils['morse'] = self.morse_code(ilsobj.ident)
                ils['localizer_course'] = ilsobj.locCourse
                ils['crossing_height'] = ilsobj.crossingHeight
                ils['has_dme'] = ilsobj.hasDme
                ils['elevation'] = ilsobj.elevation
                rw['ils'] = ils
            runways.append(rw)
        resultSet['runways'] = runways
        self.close_session(existing_session, session)
        return resultSet

    def morse_code(self, text):
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
        result = []
        for char in text:
            result.append(morseAlphabet[char])
        return " ".join(result)

