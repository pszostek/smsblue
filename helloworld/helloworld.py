import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import os


class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'new.html')
        self.response.out.write(template.render(path, {}))

class AddHandler(webapp2.RequestHandler):
    def post(self):
        self.response.out.write(self.request.get('intensity'))
        self.response.out.write(self.request.get('days_detailed_length'))
        self.response.out.write(self.request.get('days_detailed'))
        self.response.out.write(self.request.get('days_general'))

app = webapp2.WSGIApplication([
    ('/new', MainPage),
    ('/add', AddHandler)
], debug=True)


def main():
  application.RUN()


if __name__ == '__main__':
  main()
