# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 09:53:54 2017

@author: Daria komputer
"""
import math
import ephem
import requests

def iss_tle():
    tle_url = 'http://www.celestrak.com/NORAD/elements/stations.txt'
    satellite_tle = requests.get(tle_url).text
    tle_file = open('TLE_data.txt','w')
    tle_file.write(satellite_tle)
    tle_file.close()
    tle_data = open('TLE_data.txt', 'r').readlines()
    
    tle_data = [a for a in tle_data if a != '\n']
    tle_data = ''.join(tle_data)
    tle_data = tle_data.split('\n')
    names = tle_data[0::3]
    for line, value in enumerate(names[:-1], 1):
        x = str(line).strip()
        print(x, value)
    
    number = 1
    sat_number = int(number) * 3 - 3
    
    return tle_data[sat_number:sat_number+3]
   
    
tle_data=iss_tle()
tle_data1 = " ".join(tle_data[0].split())
tle_data2 = tle_data[1]
tle_data3 = tle_data[2]

obs = ephem.Observer()
obs.lat = '50.06143'
obs.long = '19.93658'
