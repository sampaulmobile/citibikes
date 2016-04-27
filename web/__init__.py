import threading
import atexit
import os
from flask import Flask, jsonify, render_template, request, send_from_directory
import geopy
import geopy.distance
import json, requests

LOOP_TIME = 60
STATUS_URL = 'https://www.citibikenyc.com/stations/json'

station_map = {}
refresh_thread = threading.Thread()


def create_app():
    app = Flask(__name__)

    def interrupt():
        global refresh_thread
        refresh_thread.cancel()

    def initData():
        global station_map
        global refresh_thread

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

        refresh_thread = threading.Timer(LOOP_TIME, refreshData, ())
        refresh_thread.start()

    def refreshData():
        global station_map
        global refresh_thread
        data = json.loads(requests.get(url=STATUS_URL).text)
        for station in data['stationBeanList']:
            o = station_map[station['id']]
            o['docks'] = station['availableDocks']
            o['bikes'] = station['availableBikes']
            o['lastUpdated'] = station['lastCommunicationTime']

        refresh_thread = threading.Timer(LOOP_TIME, refreshData, ())
        refresh_thread.start()

    initData()
    atexit.register(interrupt)
    return app

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = create_app()
from web import views

