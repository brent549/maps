#!/usr/bin/env python3

import json
import pprint
import os
import sys
import csv
from town_info import NJ_Info


def school_town_ratings():
    f = 'ratings.csv'
    d = {}
    with open(f, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #return list(csv_reader)
        for row in csv_reader:
            town = row[0]
            d[town]={}
            d[town]['School Rating']=row[1]
            d[town]['Town Rating']=row[2]
    return d
    #with open(f, mode='r') as csv_file:
    #    csv_reader = csv.DictReader(csv_file)
    #    headers = csv_reader.fieldnames
    #    for row in csv_reader:
    #        for header in headers:
    #            if header 
                
def sites(file):
    a=[]
    with open(file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                a.append(line.rstrip())
    return a

def files(dir):
    return [dir+'/'+x for x in os.listdir(dir) if (x.endswith(".json") and x.startswith('all'))]
    

def convert_to_min(s):
    #convert string to min
    # 1 hour 20 mins
    # 49 mins
    total=0
    a = s.split()

    # should be an even num
    if (len(a) % 2) != 0:
        print ("{} isnt even".s)

    if 'hour' in a[1]:
        return (int(a[0])*60) + int(a[2])
    return int(a[0])

origins = sites('etc/cities.txt')
outdir = 'json'

pprint.pprint(files(outdir))

results={}
for file in files(outdir):
    print("working on {}".format(file))
    if not os.path.isfile(file):
        print("Cant fine {} .... skipping".format(file))
        continue

    data=[]
    with open(file, "r") as fd:
        data = json.load(fd)
        pprint.pprint(data)
        
        #{origin}->{dest}->time: | distance: | mode:
        #{origin}->{dest}->[(time,distance,mode)]
         
        if 'error_message' in data:
            print(data['error_message'])
            continue

        if len(data['rows']) != len(data['origin_addresses']):
            print("diff length of lists... rows[] != origin_addresses[]".format(
                    len(data['rows']),len(data['origin_addresses'])))

        mode=data['transit_mode']
        for i, row  in enumerate(data['rows']):
            origin = data['origin_addresses'][i]
            for j, dest in  enumerate(data['destination_addresses']):

                status = row['elements'][j]['status']
                if status != 'OK':
                    print("status not OK {} ... {}".format(status,row))
                    continue
                dist = row['elements'][j]['distance']['text']
                dur  = row['elements'][j]['duration']['text']
                #print("%s -> %s" % (dist,dur))
                t=(convert_to_min(dur),dist,mode)
            
                if origin not in results:
                    results[origin]={}
                if dest not in results[origin]:
                    results[origin][dest] = []
                results[origin][dest].append(t)

#print(results)
#orig=Wyckoff, NJ 07481, USA, 
#locs={'770 Broadway, New York, NY 10003, USA': [(110, '27.5 mi', 'Rail'), (48, '29.3 mi', 'Driving'), (113, '30.9 mi', 'Bus')], '9 Charles Terrace, Waldwick, NJ 07463, USA': [(76, '7.0 mi', 'Rail'), (9, '3.4 mi', 'Driving'), (76, '7.0 mi', 'Bus')]}
for orig,locs in sorted(results.items()):
    #print("*** orig={}, locs={}".format(orig,locs))
    for loc,tups in locs.items():
        #print("\t*** loc={}, tups={}".format(loc,tups))
        l = sorted(tups, key = lambda x: x[0])
        shortest = l[0]
        if 'New York' in loc and len(l) > 1:
            shortest = l[1]
        print("{} {} {}".format(orig,loc,shortest))

nj_data = NJ_Info()
    
#Town,School Rating,Town Rating,Distance to NYC,Commute NYC,NYC Commute Method,Distance to Waldwick,Drive to Waldwick,Waldwick Commute Method
header = ['Town','School Rating','Town Rating','Commute to NYC','Distance to NYC','NYC Commute Method','Drive to Waldwick','Distance to Waldwick','Waldwick Commute Method',
'Crime rate per 1000 residents 2016',
'Violent crime rate per 1000 residents 2016',
'NJM Top High Schools rank 2018',
'Average residential tax bill 2018',
'Effective property tax rate 2018']

print(('\t').join(header))
for orig,locs in sorted(results.items()):
    #print("orig={}, locs={}".format(orig,locs))
    row = [''] * len(header)
    town = orig.split(',')[0] # strip off <town>, NJ
    row[0] = town
    town_info = nj_data.town(town)
    if town_info is None:
        print("Cant find info for {}".format(town))
        continue
    row[2] = town_info['rank']
    row[1] = town_info['njm top high schools rank 2018']

    # Get fastest travel and mode of transport
    #[(6, '2.5 mi', 'Driving'), (14, '2.0 mi', 'Bus'), (14, '2.0 mi', 'Rail')]
    for loc,tups in locs.items():
        distance_tup = sorted(tups, key = lambda x: x[0])
        shortest = distance_tup[0]
        if 'New York' in loc and len(tups) > 1:
            row[3] = str(distance_tup[1][0])
            row[4] = str(distance_tup[1][1])
            row[5] = str(distance_tup[1][2])
        else:
            row[3] = str(distance_tup[0][0])
            row[4] = str(distance_tup[0][1])
            row[5] = str(distance_tup[0][2])
        if 'Waldwick' in loc:
            row[6] = str(distance_tup[0][0])
            row[7] = str(distance_tup[0][1])
            row[8] = str(distance_tup[0][2])

    #print(town_info)
    for i,idx in enumerate(list(reversed(header))[:5]):
        pos=len(header)-i-1
        row[pos] = town_info[idx.lower()]
        
    print(('\t').join(row))
