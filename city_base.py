'''
Created on 29 Nov 2014

@author: mariaz
'''


import re

def detag(s):
    s = s.split("|")[-1]
    s = re.sub(r'[\[\]\{\}]','',s)
    return s

COMPASS = {'N':1, 'E':1, 'S':-1, 'W':-1}

def coord(c):
    degrees, rest = c.strip().split('^')
    minutes, compass = rest.split("'")
    degrees = float(degrees)
    minutes = float(minutes)
    dec = degrees + minutes/60. 
    dec *= COMPASS[compass]
    return round(dec,2)

city_base = []

with open("city_base.txt") as f:
    for line in f:
        cols = line.split('||')
        if len(cols) != 5:
            print cols
        lat,lon,city,province,country=cols
        city = detag(city)
        province = detag(province)
        country = detag(country).strip()
        lat = coord(lat)
        lon = coord(lon)
        city_base.append((lat,lon,city,province,country))
    
print city_base
print len(city_base)