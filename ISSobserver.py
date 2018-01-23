"""
Created 28-12-2017
Author: Daria Pączkowska
Program contains functions:
- iss_tle() - loads ISS TLE data
- input_location() - user input of observer location, number of calculated ISS
    passes, output only visible or all passes 
- iss_position() - calculating of ISS position realtive to defined observer
- iss_visibility() - return if ISS pass is visible
- iss_in_the_sky() - return ISS pass projection on schematic sky map
- strfdelta() - return defined date format
- output() - output data presentation   
"""

import sys
import ephem
import requests
import numpy as np
import matplotlib.pyplot as plt
import datetime
from string import Formatter
from colors import blue, cyan, green, red, magenta

#iss tle data loading
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
    for i,j in enumerate(names[:-1], 1):
        x = str(i).strip()
        j= str(j).strip()
        if j=='ISS (ZARYA)':
            number=x
    
    sat_number = int(number) * 3 - 3
    
    return tle_data[sat_number:sat_number+3]
   
# user input of iss observer position 
def input_location():
    
    locationKeyword = input(cyan('Location keyword: ')) #type first few letters of the location keywords included in the entries below
    locationName = ''
    
    if locationKeyword.lower() == 'samszyce'[0:len(locationKeyword)].lower():
        locationName = 'Samszyce'
        print()
        print('Observer in Samszyce')
        obs = ephem.Observer()
        obs.lat = '52.5997'   
        obs.long = '18.6986'     
        obs.elev = 92
    elif locationKeyword.lower() == 'włocławek'[0:len(locationKeyword)].lower():
        locationName = 'Włocławek'
        print()
        print('Observer in Włocławek')
        obs = ephem.Observer()
        obs.lat = '52.6483'   
        obs.long = '19.0677'     
        obs.elev = 60
    elif locationKeyword.lower() == 'warszawa'[0:len(locationKeyword)].lower():
        locationName = 'Warszawa'
        print()
        print('Observer in Warszawa')
        obs = ephem.Observer()
        obs.lat = '52.2297'   
        obs.long = '21.0122'     
        obs.elev = 113
    elif locationKeyword.lower() == 'userdefined'[0:len(locationKeyword)].lower():
        locationName = 'UserDefined'
        print()
        print(green('Observer position defined by user:'))
        obs = ephem.Observer()
        check = True
        while check:
            obs.lat = input(cyan('Observer latitude [xx] N or [-xx] S: '))
            if int(obs.lat) in range(-90,90):
                check = False
            else:
                print(red('Value is not in range (-90,90)'))
        check = True
        while check:
            obs.long = input(cyan('Observer longitude [xx] E or [-xx] W: '))
            if int(obs.long) in range(-180,180):
                check = False
            else:
                print(red('Value is not in range (-180,180)'))
        obs.elev = int(input(cyan('Observer elevation: ')))
    else:
        print()
        print(red('Location keyword not found.'))
        sys.exit()
    
    print()
    print(green('Enter number of ISS passes'))
    nr = int(input(cyan('Number of passes: ')))   
    print()
    print(green('Show all passes or just visible?'))
    check = True
    while check:
        pas = input(cyan('Type "all" or "v": '))
        if pas in ['all', 'v']:
            check = False
        else:
            print(red('Error. Enter "all" or "v"'))
    
    return locationName, obs.lat, obs.long, obs.elev, nr, pas 

# calculations of iss position relative to the observer 
def iss_position(iss, obs):
    
    tr, azr, tt, altt, ts, azs = obs.next_pass(iss)
    rise_time = tr.datetime()
    set_time = ts.datetime()
    duration = abs(set_time-rise_time)
    eclip = 0
    iss_alt, iss_az = [], []
    dt = datetime.timedelta(seconds=1)
    date = rise_time
    eclip_check = True
    while (date < set_time):
        obs.date=date
        iss.compute(obs)
        iss_alt.append(np.rad2deg(iss.alt))
        iss_az.append(np.rad2deg(iss.az))
        eclip = iss.eclipsed
        if eclip == False:
            eclip_check = False
        date = date + dt
         
    obs.date = tt.datetime()
    obs.date = tr + (25 * ephem.minute)

    return tr, azr, altt, ts, azs, duration, iss_alt, iss_az, eclip_check

# checking if iss pass is visible
def iss_visibility(obs, iss, altt, nr, pas, i, eclip_check):
    
    sun = ephem.Sun(obs)
    sun_alt = np.rad2deg(sun.alt)
    visible = False
    if eclip_check is False and -20 < sun_alt < -5 and np.rad2deg(altt) >= 10:
        visible = True
        print()
        print(blue('=' * 60))
        print(blue('ISS pass is visible'))
        print(cyan('-' * 60))

    if pas == 'all':  
        if eclip_check is True:
            print(magenta('=' * 60))
            print('ISS pass is not visible because ISS is eclipsed')
            print(cyan('-' * 60))
        elif np.rad2deg(altt) < 10:
            print(magenta('=' * 60))
            print('ISS pass is not visible because its altitude is below 10 deg')
            print(cyan('-' * 60))
        elif sun_alt < -20 or sun_alt > -5:
            print(magenta('=' * 60))
            print('ISS pass is not visible because of Sun position')
            print('Sun altitude = %s ' % sun_alt)
            print(cyan('-' * 60))
    
    return(visible)

# plotting iss pas in the sky projection
def iss_in_the_sky(iss_alt, iss_az):
    
    r = 90-np.array(iss_alt)
    theta = np.deg2rad(iss_az) 
    sky = plt.subplot(111, projection='polar')
    
    sky.plot(theta, r)
    sky.set_theta_zero_location("N")
    s = np.arange(10,90,10)
    sky.set_rticks(s)
    sky.set_xticklabels([ 'N \n $0\degree$', '$45\degree$', 'W \n $90\degree$', '$135\degree$', '$180\degree$ \n S', '$225\degree$', 'E \n $270\degree$', '$315\degree$'])
    ttl = sky.set_title("ISS pass in the sky projection", va="bottom")
    ttl.set_position([0.5, 1.1])
    plt.show()
    
    return()

# date formating
def strfdelta(tdelta, fmt):
    f = Formatter()
    d = {}
    l = {'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    k = list(map( lambda x: x[1], list(f.parse(fmt))))
    rem = int(tdelta.total_seconds())

    for i in ('D', 'H', 'M', 'S'):
        if i in k and i in l.keys():
            d[i], rem = divmod(rem, l[i])

    return f.format(fmt, **d)    

# output data presentation
def output(tr,ts, altt, azr, azs, duration):
    tr_local = ephem.localtime(tr)    
    ts_local = ephem.localtime(ts) 
    
    print('Rise time: %s' % tr_local.isoformat(sep=' ', timespec='seconds'))
    print('Set time: %s' % ts_local.isoformat(sep=' ', timespec='seconds'))
    print('Max altitude: %.2f deg' % np.rad2deg(altt))
    print('Rise azimuth: %.2f deg' % np.rad2deg(azr))
    print('Set azimuth: %.2f deg' % np.rad2deg(azs))
    print(strfdelta(duration, "Duration: {M} min {D} s"))
    print(cyan('-' * 60))
    
    iss_in_the_sky(iss_alt, iss_az)
    return()
    
# Main program
    
print(blue('='*60))
print(blue('Program for ISS observations'))
print(blue('='*60))
print()
print('-'*60)
print(blue('Program shows parameters of ISS passes above defined observer'))
print(blue('ISS position is calculated based on TLE data from: \nhttps://www.celestrak.com/NORAD/elements/stations.txt'))
print('-'*60)

# loading tle data
tle_data=iss_tle()
tle_data1 = " ".join(tle_data[0].split())
tle_data2 = tle_data[1]
tle_data3 = tle_data[2]
iss = ephem.readtle(tle_data1, tle_data2,tle_data3)

# observer calculations
obs = ephem.Observer()

print()
print(green('Choose your position from defined positions or enter your coordinates.'))
print()
print(green('Type first few letters of selected option:'))
print()
print(green('Samszyce, Włocławek, Warszawa, UserDefined'))

locationName, obs.lat, obs.long, obs.elev, nr, pas = input_location()

# setting as starting date for observation 'now'
now = datetime.datetime.utcnow()
obs.date= now

for i in range(nr):
    
    tr, azr, altt, ts, azs, duration, iss_alt, iss_az, eclip_check = iss_position(iss, obs)
    
    if pas == 'v':
        visible = iss_visibility(obs, iss, altt, nr, pas, i, eclip_check)
        if visible == True:
            output(tr,ts, altt, azr, azs, duration)
        else:
            if i == nr-1:
                print()
                print(magenta('No visible ISS passes occure'))
    else:
        visible = iss_visibility(obs, iss, altt, nr, pas, i, eclip_check)
        output(tr,ts, altt, azr, azs, duration)

# if any iss pass is visible calculate until visible pass will occure
if pas == 'v':
    if visible == False:
        print()
        print("You have to wait for visible ISS pass until:")
        check = True
        while check:
            tr, azr, altt, ts, azs, duration, iss_alt, iss_az, eclip_check = iss_position(iss, obs)
            visible = iss_visibility(obs, iss, altt, nr, pas, i, eclip_check)
            if visible == True:
                check = False
            else:
                check = True
        output(tr,ts, altt, azr, azs, duration)        