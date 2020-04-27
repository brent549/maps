#!/usr/bin/env python3

import json
import pprint
import os
import sys
import csv


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

origins = sites('cities.txt')
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
for orig,locs in sorted(results.items()):
    for loc,tups in locs.items():
        l = sorted(tups, key = lambda x: x[0])
        shortest = l[0]
        if 'New York' in loc:
            shortest = l[1]
        print("{} {} {}".format(orig,loc,shortest))

ratings = school_town_ratings()
    
#Town,School Rating,Town Rating,Distance to NYC,Commute NYC,NYC Commute Method,Distance to Waldwick,Drive to Waldwick,Waldwick Commute Method
header = ['Town','School Rating','Town Rating','Distance to NYC','Commute NYC','NYC Commute Method','Distance to Waldwick','Drive to Waldwick','Waldwick Commute Method']
print(('\t').join(header))
for orig,locs in sorted(results.items()):
    alist = [''] * 9
    alist[0] = orig.split(',')[0]
    if alist[0] in ratings:
        alist[1] = ratings[alist[0]]['School Rating']
        alist[2] = ratings[alist[0]]['Town Rating']
    #[(6, '2.5 mi', 'Driving'), (14, '2.0 mi', 'Bus'), (14, '2.0 mi', 'Rail')]
    for loc,tups in locs.items():
        l = sorted(tups, key = lambda x: x[0])
        shortest = l[0]
        if 'New York' in loc:
            alist[3] = str(l[1][0])
            alist[4] = str(l[1][1])
            alist[5] = str(l[1][2])
        if 'Waldwick' in loc:
            alist[6] = str(l[0][0])
            alist[7] = str(l[0][1])
            alist[8] = str(l[0][2])
    print(('\t').join(alist))
