'''
Created on 29 Nov 2014

@author: mariaz
'''

from city_db import CITY_DB
import random

c = random.choice(CITY_DB)
print c, c[2].decode('utf-8')

if __name__ == '__main__':
    pass