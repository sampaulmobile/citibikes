from flask import Flask, jsonify, render_template, request, send_from_directory
from web import app, station_map
import geopy
import geopy.distance
from heapq import heappush, heappop, nsmallest


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status/<location>')
def status(location):
    lon, lat = location.split(';')[0:2]
    pt = geopy.Point(longitude=lon, latitude=lat)
    # input_pt = geopy.Point(longitude=-74.005947, latitude=40.745295)
    return jsonify(output=getStations(pt))

def getStations(input_pt, n = 5):
    heap = []
    for i, d in station_map.iteritems():
        dist = geopy.distance.distance(input_pt, d['pt']).km
        heappush(heap, (dist,i))
        # resize heap?
    output = []
    for pair in nsmallest(n, heap):
        dist, s_id = pair
        o = station_map[s_id]
        output.append({
            'address' : o['address'],
            'bikes' : o['bikes'],
            'docks' : o['docks'],
            'dist' : dist,
            'lastUpdated' : o['lastUpdated']
            })
    return output
