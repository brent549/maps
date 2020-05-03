#!/usr/bin/env python3

import json
import pprint
import os


def sites(file):
    a=[]
    with open(file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                a.append(line.rstrip())
    return a

def files(dir):
    return [x for x in os.listldir(outdir) if x.endswith(".json") and not x.beginswith('all')]
    

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

results={}
for o in origins:
    print(o)
    file="%s/%s.json" % (outdir,o.replace(' ','_').replace(',',''))
    if not os.path.isfile(file):
        continue

    with open(file, "r") as fd:
        data=[]
        for line in fd:
            data.append(json.loads(line.strip()))
        pprint.pprint(data)
        
        #{origin}->{dest}->time: | distance: | mode:
        #{origin}->{dest}->[(time,distance,mode)]
        for x in data:
            if 'error_message' in x:
                print(x['error_message'])
                continue
            mode=x['transit_mode']
            origin=x['origin_addresses'][0]
            d = x['rows'][0]['elements']
            if origin not in results:
                results[origin] = {}
            for i in range(len(d)):
                print(d[i])
                dist = d[i]['distance']['text']
                dur = d[i]['duration']['text']
                dest = x['destination_addresses'][i]
                #print("%s -> %s" % (dist,dur))
                t=(convert_to_min(dur),dist,mode)
                if dest not in results[origin]:
                    results[origin][dest] = []
                results[origin][dest].append(t)

print(results)
for orig,locs in results.items():
    for loc,tups in locs.items():
        l = sorted(tups, key = lambda x: x[0])         
        shortest = l[0]
        if 'New York' in loc:
            shortest = l[1]
        print("{} {} {}".format(orig,loc,shortest))
    
