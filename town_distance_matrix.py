#!/usr/bin/env python3

# Take a list of destinations and get driving, bus and tail commute times.
# Write the data to outdir
# list of towns are gatheres from town_info.py

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
from town_info import NJ_Info


API_KEY=''
with open('etc/key.txt') as f:
    API_KEY=f.read().strip()
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
        'origins': '|'.join(src),
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
        'origins': '|'.join(src),
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
        'origins': '|'.join(src),
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
        return mode.split('|')[0].title()
    return mode.title()

def sites(file):
    a=[]
    with open(file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                a.append(line.rstrip())
    return a


#all_origins = sites('etc/cities.txt')
nji = NJ_Info()
all_origins = [ town + ', NJ' for town in nji.towns('Bergen').keys()]

if not os.path.isdir(outdir):
    print("{} is not a directory".format(outdir))
    sys.exit()

# Google only allows 25 origin/destinatinos at a time
for i in range(0,len(all_origins),25):
    origins = all_origins[i:i+25]
    for url in car_url(origins), bus_url(origins), train_url(origins):
        transit_mode=transitmode(url)
        file="%s/%s_%s_%s.json" % (outdir,'all_cities',i,transit_mode)
        with open(file, "w") as fd:
            response = http.request('GET', url)
            print(response.status)
            data = json.loads(response.data.decode('utf-8'))
            data['transit_mode']=transit_mode
            pprint.pprint(data)
            json.dump(data, fd)
