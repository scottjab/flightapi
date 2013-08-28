#!/usr/bin/env python

from bs4 import BeautifulSoup

import pymetar
import requests
from pymetar import NetworkException

# Weather methods.

def get_taf(station):
    taf_service = "http://weather.noaa.gov/cgi-bin/mgettaf.pl?cccc=%s"
    try:
        parsed_html = BeautifulSoup(requests.get(taf_service % station).content)
        parsed_taf = parsed_html.find('pre').text
        parsed_taf = parsed_taf.replace('\n', '')
        return parsed_taf
    except Exception as e:
        raise e


def get_parsed_metar(station):
    report = ""
    try:
        fetcher = pymetar.ReportFetcher(station)
        rep = fetcher.FetchReport()
        report = pymetar.ReportParser().ParseReport(rep)
        return report
    except NetworkException as e:
        raise e
    return str(report)


def metar_as_dict(metar):
    report = {}
    report['cloud_info'] = metar.getCloudinfo()
    report['cloud_type'] = metar.getCloudtype()
    report['conditions'] = metar.getConditions()
    report['cycle'] = metar.getCycle()
    report['dew_point_c'] = metar.getDewPointCelsius()
    report['dew_point_f'] = metar.getDewPointFahrenheit()
    report['full_report'] = metar.getFullReport()
    report['humidity'] = metar.getHumidity()
    report['iso_time'] = metar.getISOTime()
    report['pixmap'] = metar.getPixmap()
    report['pressure'] = metar.getPressure()
    report['pressure_hg'] = metar.getPressuremmHg()
    report['raw_metar'] = metar.getRawMetarCode()
    report['report_url'] = metar.getReportURL()
    report['sky_conditions'] = metar.getSkyConditions()
    report['station_alt'] = metar.getStationAltitude()
    report['station_city'] = metar.getStationCity()
    report['station_country'] = metar.getStationCountry()
    report['station_lat'] = metar.getStationLatitude()
    report['station_lat_f'] = metar.getStationLatitudeFloat()
    report['station_lon'] = metar.getStationLongitude()
    report['station_lon_f'] = metar.getStationLongitudeFloat()
    report['station_name'] = metar.getStationName()
    report['station_pos'] = metar.getStationPosition()
    report['station_pos_f'] = metar.getStationPositionFloat()
    report['temp'] = metar.getTemperatureCelsius()
    report['temp_f'] = metar.getTemperatureFahrenheit()
    report['time'] = metar.getTime()
    report['vis_k'] = metar.getVisibilityKilometers()
    report['vis'] = metar.getVisibilityMiles()
    report['weather'] = metar.getWeather()
    report['wind_compus'] = metar.getWindCompass()
    report['wind_direction'] = metar.getWindDirection()
    report['wind_speed'] = metar.getWindSpeed()
    report['wind_speed_beaufort'] = metar.getWindSpeedBeaufort()
    report['wind_speed_knots'] = metar.getWindSpeedKnots()
    report['wind_speed_mph'] = metar.getWindSpeedMilesPerHour()
    report['windchill'] = metar.getWindchill()
    report['windchill'] = metar.getWindchillF()
    return report
