import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
from city_db import CITY_DB
import random

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with author, content, and date."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
        
class Guess(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guess = self.request.get('guess')
        answer = int(self.request.get('answer'))
        result = "Correct!!" if CITY_DB[answer][2].decode('utf-8') == guess.split(",")[0] else "Incorrect - that was " + CITY_DB[answer][2]
        query_params = {"result": result, "id": random.randrange(len(CITY_DB))}
        self.redirect('/photos?' + urllib.urlencode(query_params))

class Browse(webapp2.RequestHandler):
    
    def get(self):
        template_values = {
            'cities': enumerate(CITY_DB)
        }

        template = JINJA_ENVIRONMENT.get_template('cities.html')
        self.response.write(template.render(template_values))

class Photos(webapp2.RequestHandler):
    def jitter(self):
        return random.random() / 10 - 0.05
        
    def genOptions(self, count):
        uniq = set()
        while len(uniq) < count:
            choice = random.randrange(len(CITY_DB))
            if choice not in uniq:
                uniq.add(choice)

        return [(city_id, CITY_DB[city_id][2], CITY_DB[city_id][4]) for city_id in uniq]            

    def get(self):
        city_id = int(self.request.get("id", random.randrange(len(CITY_DB))))

        city = CITY_DB[city_id]
        lat = self.request.get("lat")
        lon = self.request.get("lon")
        lat = lat if lat else city[0]
        lon = lon if lon else city[1]
        lat = float(lat) + self.jitter()
        lon = float(lon) + self.jitter()
        options = self.genOptions(5)
        options += [(city_id, city[2], city[4])]
        random.shuffle(options)
        template_values = {
            'coord': "{0}|{1}".format(lat, lon),
            'city': city,
            'options' : options,
            'id' : city_id,
            'result' : self.request.get("result"),
        }

        template = JINJA_ENVIRONMENT.get_template('photos.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', Photos),
    ('/sign', Guestbook),
    ('/browse', Browse),
    ('/photos', Photos),
    ('/guess', Guess),
], debug=True)
