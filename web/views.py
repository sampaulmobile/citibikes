from flask import Flask, jsonify, render_template, request, send_from_directory
from web import app, station_map
import geopy
import geopy.distance
from heapq import heappush, heappop, nsmallest
from datetime import datetime
from pytz import timezone
from dateutil import tz
import time
import json, requests

STATUS_URL = 'https://www.citibikenyc.com/stations/json'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status/<location>')
def status(location):
    lat, lon = location.split(';')[0:2]
    pt = geopy.Point(longitude=lon, latitude=lat)
    return jsonify(output=getStations(pt))

@app.route('/status_full/<location>')
def status_full(location):
    station_map = {}
    data = json.loads(requests.get(url=STATUS_URL).text)
    for station in data['stationBeanList']:
        station_map[station['id']] = {
                'name' : station['stationName'],
                'address' : station['stAddress1'],
                'pt' : geopy.Point(longitude=station['longitude'], latitude=station['latitude']),
                'docks' : station['availableDocks'],
                'bikes' : station['availableBikes'],
                'lastUpdated' : station['lastCommunicationTime']
                }
    lat, lon = location.split(';')[0:2]
    pt = geopy.Point(longitude=lon, latitude=lat)
    return jsonify(output=getStationsWithMap(pt, station_map))

def getStationsWithMap(input_pt, station_map, n = 5):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Eastern')
    heap = []
    for i, d in station_map.iteritems():
        dist = geopy.distance.distance(input_pt, d['pt']).km
        heappush(heap, (dist,i))
        # resize heap?
    output = []
    for pair in nsmallest(n, heap):
        dist, s_id = pair
        o = station_map[s_id]
        ts = datetime.strptime(o['lastUpdated'], "%Y-%m-%d %I:%M:%S %p")
        t = ts.replace(tzinfo=to_zone).astimezone(to_zone)
        now = datetime.now(timezone('US/Eastern'))
        secs = int(round((now - t).total_seconds()))

        output.append({
            'address' : o['address'],
            'bikes' : o['bikes'],
            'docks' : o['docks'],
            'dist' : dist,
            'timeOffset' : secs,
            'lastUpdated' : "{0}s".format(secs)
            })
    return output

def getStations(input_pt, n = 5):
    global station_map
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Eastern')

    heap = []
    for i, d in station_map.iteritems():
        dist = geopy.distance.distance(input_pt, d['pt']).km
        heappush(heap, (dist,i))
        # resize heap?
    output = []
    for pair in nsmallest(n, heap):
        dist, s_id = pair
        o = station_map[s_id]
        ts = datetime.strptime(o['lastUpdated'], "%Y-%m-%d %I:%M:%S %p")
        t = ts.replace(tzinfo=to_zone).astimezone(to_zone)
        now = datetime.now(timezone('US/Eastern'))
        secs = int(round((now - t).total_seconds()))

        output.append({
            'address' : o['address'],
            'bikes' : o['bikes'],
            'docks' : o['docks'],
            'dist' : dist,
            'timeOffset' : secs,
            'lastUpdated' : "{0}s".format(secs)
            })
    return output
