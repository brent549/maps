#!/usr/local/bin/python2

# Written to find the distance from a person to the closest office.  This was used during an 
# exercise to get remote workers to move back into the nearest office.  Ironic that COVID changed
# that strategy

import urllib2
import urllib
import json
import csv
import requests
import datetime
import sys
import os

API_KEY=''
BASE_URL='https://maps.googleapis.com/maps/api/distancematrix/json'


origins=[]
destinations=[]


def next_monday():
    today = datetime.date.today()
    monday = today + datetime.timedelta( (0-today.weekday()) % 7 )
    return monday 

def next_weekday(d,weekday):
    ''' d = datetime.date(2018,2,4)
        next_monday = next_weekday(d,0) # 0 = monday '''
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # target day already happened
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def arrival_time(d):
    ''' Return epoch of 9am of the apporpriate time zone
        to represent the arrival time to the office during commute hours '''
    pass


def sites(file):
    a=[]
    with open(file,'rb') as csvfile:
        myreader = csv.DictReader(csvfile, delimiter=',')
        header =  myreader.fieldnames
        for row in myreader:
            a.append("%s %s, %s" % (row['Street'],row['City'],row['State']))
    return a

def get_people(file):
    #a=[]
    d={}
    with open(file,'rb') as csvfile:
        myreader = csv.DictReader(csvfile, delimiter=',')
        header =  myreader.fieldnames
        for row in myreader:
            site="%s, %s" % (row['City'],row['State'])
            person="%s %s" % (row['First'],row['Last'])
            #a.append("%s, %s" % (row['City'],row['State']))
            #print gen_url(site)
            d[person]=site
    return d

def gen_url(src):
    args={
        #'origins':'|'.join(origins), 
        'origins': src,
        'destinations':'|'.join(destinations) ,
        'mode': 'driving',
        'units': 'imperial',
        'traffic_model': 'best_guess',
        #'arrival_time': '1519056000',  # mon feb 19th 2018 10am CST
        'departure_time':'now',
        'key': API_KEY ,}

    url = BASE_URL + '?' + urllib.urlencode(args)
    return url

def analysis(j):

    home=j['origin_addresses'][0]
    for i in range(len(j['rows'][0]['elements'])):
        office=j['destination_addresses'][i]
        distance=j['rows'][0]['elements'][i]['distance']['text']
        duration=j['rows'][0]['elements'][i]['duration']['text']
        status=j['rows'][0]['elements'][i]['status']
        print "%s,%s,%s,%s,%s" % (home,office,distance,duration,status)

destinations=sites('sites.csv')
people=get_people('people.csv')

for p,s in people.items():
    file="%s/%s.json" % ('json',p.replace(' ','_'))
    data=''
    if os.path.isfile(file):
        with open(file,"r") as fd:
            data=json.load(fd)
    else:
        url=gen_url(s)
        response=requests.get(url)
        data=response.json()
     
        with open(file,"w") as fd:
            json.dump(data,fd)
    analysis(data)

#fd=open('json.txt','rb')
#analysis(json.load(fd))
