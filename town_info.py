#!/usr/bin/env python3 

import csv
import pprint

class NJ_Info(object):
    def __init__(self, confdir='etc', 
                town_file='NJ-TOP-TOWNS-2019.csv',
                school_file='NJ-Full-Schools-2018.csv',
            ):
        self.confdir = confdir
        self.town_file = town_file
        self.school_file = school_file # TODO turn this into a dict
        self.town_data = self.load_csv(confdir + '/' + town_file)

    # read csv file return dict of dict
    # dict['town']={k:v, k1:v1,...}
    def load_csv(self, csv_file):
        result={}
        with open(csv_file, 'r') as fd:
            myreader = csv.DictReader(fd, delimiter=',')
            header = myreader.fieldnames
            for row in myreader:
                if 'Municipality' not in row: 
                    print("Cant find key 'Municipality' .. skipping")
                    continue

                town = row['Municipality'].lower()
                # key on town and make everyting lower case
                result[town]={x.lower():y for x,y in row.items()}

                # make int
                for key in 'rank', 'njm top high schools rank 2018':
                    if key in result:
                        result[town][key]=int(result[town][key])

                # make float
                for key in 'crime rate per 1000 residents 2016':
                    if key in result:
                        result[town][key]=float(result[town][key])
        return result

    def towns(self,county=None):
        if county is not None:
            #x for x,y in self.town_data.items() if self.town_data[x]['county'] == county
            #return [x for x,y in self.town_data.items() if y['county'] == county]
            return {x:y for x,y in self.town_data.items() if y['county'].lower() == county.lower()}
        return self.town_data

    def town(self,name):
        name = name.lower()
        if name in self.town_data:
            return self.town_data[name]
        return None


if __name__ == '__main__':
    a = NJ_Info()
    pprint.pprint(a.towns())
    print("---------------")
    pprint.pprint(a.towns('bergen'))
