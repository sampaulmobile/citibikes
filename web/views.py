from flask import Flask, jsonify, render_template, request, send_from_directory
from web import app, station_map
import geopy
import geopy.distance
from heapq import heappush, heappop, nsmallest
from datetime import datetime
from pytz import timezone
from dateutil import tz
import time



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status/<location>')
def status(location):
    lon, lat = location.split(';')[0:2]
    pt = geopy.Point(longitude=lon, latitude=lat)
    return jsonify(output=getStations(pt))

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
        secs = round((now - t).total_seconds())

        output.append({
            'address' : o['address'],
            'bikes' : o['bikes'],
            'docks' : o['docks'],
            'dist' : dist,
            'lastUpdated' : "{0} secs".format(secs)
            })
    return output
