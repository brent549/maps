#!/usr/bin/env python3

import urllib
import urllib3
import json
import csv
import requests
import datetime
import time
import calendar
import pprint
import pytz
import sys
import os
#import urllib.parse as urlparse
from urllib.parse import urlparse, parse_qs


API_KEY=''
BASE_URL='https://maps.googleapis.com/maps/api/distancematrix/json'

origins = []
destinations = ['9 Charles Ter Waldwick, NJ','770 Broadway New York, NY']
eastern = pytz.timezone('US/Eastern')
http = urllib3.PoolManager(timeout=2.0)
outdir = 'json'


def next_monday():
    today = datetime.date.today()
    monday = today + datetime.timedelta( (0-today.weekday()) % 7 )
    return monday

def monday_morning(hr=8):
    # Arrive monday 8 am Eastern time
    # 1587366000 == 4/20/2020 7am EST
    # 1587384000 == 4/20/2020 8am EST (GMT-4)
    # 1587387600 == 4/20/2020 9am EST (GMT-4)
    dd = datetime.datetime.combine(next_monday(),datetime.time(hr,0,tzinfo=eastern))
    return int(time.mktime(dd.timetuple()))

def next_weekday(d,weekday):
    ''' d = datetime.date(2018,2,4)
        next_monday = next_weekday(d,0) # 0 = monday '''
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # target day already happened
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def car_url(src):
    args={
        'origins': src,
        'destinations':'|'.join(destinations) ,
        'mode': 'driving',
        'units': 'imperial',
        'traffic_model': 'best_guess',
        'departure_time': monday_morning(7),
        'key': API_KEY ,}

    url = BASE_URL + '?' + urllib.parse.urlencode(args)
    return url

def bus_url(src):
    args={
        'origins': src,
        'destinations':'|'.join(destinations) ,
        'mode': 'transit',
        'transit_mode': 'bus|subway',
        'units': 'imperial',
        'traffic_model': 'best_guess',
        'arrival_time': monday_morning(8),
        'key': API_KEY ,}

    url = BASE_URL + '?' + urllib.parse.urlencode(args)
    return url

def train_url(src):
    args={
        'origins': src,
        'destinations':'|'.join(destinations) ,
        'mode': 'transit',
        'transit_mode': 'rail',
        'units': 'imperial',
        'traffic_model': 'best_guess',
        'arrival_time': monday_morning(8),
        'key': API_KEY ,}

    url = BASE_URL + '?' + urllib.parse.urlencode(args)
    return url

def transitmode(url):
    d = parse_qs(urlparse(url).query)
    mode = 'Driving'

    #if 'mode' in d:
    #    print("mode ",d["mode"])
    #if 'traffic_model' in d:
    #    print("traffic_model ",d["traffic_model"])
    if 'transit_mode' in d:
        #print("transit_mode ",d["transit_mode"])
        if isinstance(d['transit_mode'], list):
            mode = d["transit_mode"][0]
        else:
            mode = d["transit_mode"]
        
    if '|' in mode:
        return mode.split('|')[0]
    return mode

def sites(file):
    a=[]
    with open(file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                a.append(line.rstrip())
    return a


origins = sites('cities.txt')
for o in origins:
    file="%s/%s.json" % (outdir,o.replace(' ','_').replace(',',''))
    with open(file, "w") as fd:
        pp = pprint.PrettyPrinter(stream=fd)
        for url in car_url(o), bus_url(o), train_url(o):
            print(url)
            response = http.request('GET', url)
            #response.status
            data = json.loads(response.data.decode('utf-8'))
            data['transit_mode']=transitmode(url)
            pprint.pprint(data)
            #pp.pprint(data)
            json.dump(data, fd)
            fd.write('\n')
