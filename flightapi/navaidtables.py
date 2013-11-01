#!/usr/bin/env python

# This shit is whack.

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SurfaceType(Base):
    __tablename__ = 'SurfaceTypes'

    surfaceType = Column('SurfaceType', String(length=3), primary_key=True)
    description = Column('Description', String(length=255))


class ILS(Base):
    __tablename__ = 'ILSes'

    id = Column('ID', Integer(length=11), primary_key=True)
    runwayID = Column('RunwayID',
                      Integer(length=11),
                      ForeignKey("Runways.ID"),
                      nullable=False)

    freq = Column('Freq', Integer(length=11))
    gsAngle = Column('GsAngle', Float)
    latitude = Column('Latitude', Float)
    longitude = Column('Longtitude', Float)
    category = Column('Category', Integer(length=4))
    ident = Column('Ident', String(length=5))
    locCourse = Column('LocCourse', Float)
    crossingHeight = Column('CrossingHeight', Integer(length=4))
    hasDme = Column('HasDme', Integer(length=1))
    elevation = Column('Elevation', Integer(length=11))


class Runway(Base):
    __tablename__ = 'Runways'

    id = Column('ID', Integer(length=11), primary_key=True)
    airportID = Column('AirportID',
                       Integer(length=11),
                       ForeignKey('Airports.ID'),
                       nullable=False)
    ident = Column('Ident', String(length=3))
    trueHeading = Column('TrueHeading', Float)
    length = Column('Length', Integer(length=11))
    width = Column('Width', Integer(length=11))
    surface = Column('Surface',
                     String(length=3),
                     ForeignKey('SurfaceTypes.SurfaceType'))
    latitude = Column('Latitude', Float)
    longitude = Column('Longtitude', Float)
    elevation = Column('Elevation',
                       Integer(length=11))
    ils = relationship(ILS)
    surfaceType = relationship(SurfaceType)
    airport = relationship('Airport',
                           backref=backref('Runway'))


class Airport(Base):
    __tablename__ = 'Airports'

    id = Column('ID', Integer(length=11), primary_key=True)
    name = Column('Name', String(length=38))
    icao = Column('ICAO', String(length=4))
    primaryID = Column('PrimaryID', Integer(length=11))
    latitude = Column('Latitude', Float)
    longitude = Column('Longtitude', Float)
    elevation = Column('Elevation', Integer(length=11))
    runways = relationship(Runway)


class Airway(Base):
    __tablename__ = 'Airways'

    id = Column('ID', Integer(length=11), primary_key=True)
    ident = Column('Ident', String(length=6))


class AirwayLeg(Base):
    __tablename__ = 'AirwayLegs'

    id = Column('ID', Integer(length=11), primary_key=True)
    airwayID = Column('AirwayID', Integer(length=11), ForeignKey('Airways.ID'))
    level = Column('Level', String(length=1))
    waypoint1ID = Column('Waypoint1ID',
                         Integer(length=11),
                         ForeignKey('Waypoints.ID'))
    waypoint2ID = Column('Waypoint2ID',
                         Integer(length=11),
                         ForeignKey('Waypoints.ID'))
    isStart = Column('IsStart', Integer(length=1))
    isEnd = Column('IsEnd', Integer(length=1))
    airway = relationship(Airway)


class NavaidLookup(Base):
    __tablename__ = 'NavaidLookup'

    ident = Column('Ident', String(length=4), primary_key=True)
    type = Column('Type', Integer(length=4), primary_key=True)
    country = Column('Country', String(length=2), primary_key=True)
    navKeyCode = Column('NavKeyCode', Integer(length=4), primary_key=True)
    id = Column('ID', Integer(length=11))


class NavaidType(Base):
    __tablename__ = 'NavaidTypes'

    type = Column('Type', Integer(length=4), primary_key=True)
    desc = Column('Desc', String(length=24))


class Navaid(Base):
    __tablename__ = 'Navaids'

    id = Column('ID', Integer(length=11), primary_key=True)
    ident = Column('Ident', String(length=4))
    type = Column('Type', Integer(length=4))
    name = Column('Name', String(length=38))
    freq = Column('Freq', Integer(length=11))
    channel = Column('Channel', String(length=4))
    usage = Column('Usage', String(length=1))
    latitude = Column('Latitude', Float)
    longitude = Column('Longtitude', Float)
    elevation = Column('Elevation', Integer(length=11))
    slavedVar = Column('SlavedVar', Float)


class Terminal(Base):
    __tablename__ = 'Terminals'

    id = Column('ID', Integer(length=11), primary_key=True)
    airportID = Column('AirportID', Integer(length=11), ForeignKey(Airport))
    proc = Column('Proc', Integer(length=4))
    icao = Column('ICAO', String(length=4))
    fullName = Column('FullName', String(length=28))
    name = Column('Name', String(length=8))
    rwy = Column('Rwy', String(length=3))
    rwyID = Column('RwyID', Integer(length=11), ForeignKey(Runway))


class TrmLegType(Base):
    __tablename__ = 'TrmLegTypes'

    code = Column('Code', String(length=2), primary_key=True)
    description = Column('Description', String(length=100))


class Waypoint(Base):
    __tablename__ = 'Waypoints'

    id = Column('ID', Integer(length=11), primary_key=True)
    ident = Column('Ident', String(length=5))
    collocated = Column('Collocated', Integer(length=1))
    name = Column('Name', String(length=25))
    latitude = Column('Latitude', Float)
    longitude = Column('Longtitude', Float)
    navaidID = Column('NavaidID', Integer(length=11), ForeignKey("Navaids.ID"))
    navaid = relationship(Navaid)


class TerminalLeg(Base):
    __tablename__ = 'TerminalLegs'

    id = Column('ID', Integer(length=11), primary_key=True)
    terminalID = Column('TerminalID', Integer(length=11), ForeignKey(Terminal))
    type = Column('Type', String(length=1), ForeignKey(TrmLegType))
    transition = Column('Transition', String(length=5))
    trackCode = Column('TrackCode', String(length=2))
    wptID = Column('WptID', Integer(length=11), ForeignKey(Waypoint))
    wptLat = Column('WptLat', Float)
    wptLon = Column('WptLon', Float)
    turnDir = Column('TurnDir', String(length=1))
    navID = Column('NavID', Integer(length=11), ForeignKey(Navaid))
    navLat = Column('NavLat', Float)
    navLon = Column('NavLon', Float)
    navBear = Column('NavBear', Float)
    navDist = Column('NavDist', Float)
    course = Column('Course', Float)
    distance = Column('Distance', Float)
    alt = Column('Alt', String(length=12))
    vnav = Column('Vnav', Float)
    centerID = Column('CenterID', Integer(length=11))
    centerLat = Column('CenterLat', Float)
    centerLon = Column('CenterLon', Float)


class TerminalLegsEx(Base):
    __tablename__ = 'TerminalLegsEx'

    id = Column('ID', Integer(length=11), primary_key=True)
    isFlyOver = Column('IsFlyOver', Integer(length=1))
    speedLimit = Column('SpeedLimit', Float)


class WaypointLookup(Base):
    __tablename__ = 'WaypointLookup'

    ident = Column('Ident', String(length=5), primary_key=True)
    country = Column('Country', String(length=2), primary_key=True)
    id = Column('ID', Integer(length=11), primary_key=True)


class config(Base):
    __tablename__ = 'config'

    key = Column('key', String(length=50), primary_key=True)
    val = Column('val', String(length=50))


def main():
    engine = create_engine('mysql+mysqldb://vatsim:PASSWORD@localhost/navdata', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
if __name__ == '__main__':
    main()
