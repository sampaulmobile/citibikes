import geopy
import geopy.distance
import json, requests
from heapq import heappush, heappop, nsmallest
import threading

LOOP_TIME = 60
STATUS_URL = 'https://www.citibikenyc.com/stations/json'


class CitibikeStatus:
    def __init__(self):
        self.station_map = {}
        self.initData()
        self.refresh_thread = threading.Thread()
        self.refresh_thread = threading.Timer(LOOP_TIME, refreshData, ())
        self.refresh_thread.start()

    def initData(self):
        data = json.loads(requests.get(url=STATUS_URL).text)
        for station in data['stationBeanList']:
            self.station_map[station['id']] = {
                    'name' : station['stationName'],
                    'address' : station['stAddress1'],
                    'pt' : geopy.Point(longitude=station['longitude'], latitude=station['latitude']),
                    'docks' : station['availableDocks'],
                    'bikes' : station['availableBikes'],
                    'lastUpdated' : station['lastCommunicationTime']
                    }

    def refreshData(self):
        data = json.loads(requests.get(url=STATUS_URL).text)
        for station in data['stationBeanList']:
            o = self.station_map[station['id']]
            o['docks'] = station['availableDocks']
            o['bikes'] = station['availableBikes']
            o['lastUpdated'] = station['lastCommunicationTime']

        self.refresh_thread = threading.Timer(LOOP_TIME, refreshData, ())
        self.refresh_thread.start()

    def getStations(self, input_pt, n = 3):
        heap = []
        for i, d in station_map.iteritems():
            dist = geopy.distance.distance(input_pt, d['pt']).km
            heappush(heap, (dist,i))
            # resize heap?
        return nsmallest(n, heap)

    def printStations(self, input_pt, n = 3):
        for pair in self.getStations(input_pt, n):
            dist, s_id = pair
            o = station_map[s_id]
            print "{0} -> {1} bikes/{2} docks - dist: {3}".format(o['address'], o['bikes'], o['docks'], dist)

    #set timer to run refreshData() every 1 minutes

input_pt = geopy.Point(longitude=-74.005947, latitude=40.745295)
cs = CitibikeStatus()
ids = cs.getStations(input_pt, 7)

