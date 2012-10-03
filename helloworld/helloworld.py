import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.api import users
from webapp2_extras.appengine.users import login_required
import webapp2
import os

class Notification(db.Model):
    user = db.UserProperty()
    active = db.BooleanProperty()
    intensity = db.IntegerProperty()
    days_detailed = db.IntegerProperty()
    days_general = db.IntegerProperty()
    general_t_high = db.BooleanProperty()
    general_t_low = db.BooleanProperty()
    general_wind = db.BooleanProperty()
    general_uv_index = db.BooleanProperty()
    general_sunshine = db.BooleanProperty()
    general_precipitation = db.BooleanProperty()
    detailed_hours = db.ListProperty(int)
    detailed_temperature = db.BooleanProperty()
    detailed_temp_feels_like = db.BooleanProperty()
    detailed_wind = db.BooleanProperty()
    detailed_wind_gusts = db.BooleanProperty()
    detailed_humidity = db.BooleanProperty()
    detailed_precip = db.BooleanProperty()
    detailed_precip_prob = db.BooleanProperty()
    url = db.StringProperty()

class NotificationCounter(db.Model):
    user = db.UserProperty()
    notification = db.ReferenceProperty(Notification)
    datetime = db.DateTimeProperty()
    
class UserBalance(db.Model):
    user = db.UserProperty()
    balance = db.IntegerProperty()

class ListNotification(webapp2.RequestHandler):
    pass

#@login_required
class NewNotification(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        path = os.path.join(os.path.dirname(__file__), 'new.html')
        self.response.out.write(template.render(path, {'user':user}))

class NotificationAdded(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        key = db.Key.from_path('Notification', str(user))
        notification = Notification(parent=key)
        active = (self.request.get("active") == "active")
        notification.active = active
        intensity = self.request.get('intensity')
        if intensity == "24_hours":
            notification.intensity = 24
        elif intensity == "2_days":
            notification.intensity = 48
        elif intensity == "5_days":
            notification.intensity = 120
        else:
            notification.intensity = 168
        hours = self.request.get_all("detailed_hours")
        for hour in hours:
            notification.detailed_hours.appen(hour)

        notification.days_general = int(self.request.get('days_general_length'))
        notification.days_detailed = int(self.request.get('days_detailed_length'))
        
        days_general = self.request.get_all("days_general")
        for opt in days_general:
            if opt == "t_high":
                notification.general_t_high = True
            elif opt == "t_low":
                notification.general_t_low = True
            elif opt == "wind":
                notification.general_wind = True
            elif opt == "uv_index":
                notification.general_uv_index = True
            elif opt == "sunshine":
                notification.general_sunshine = True
            elif opt == "precipitation":
                notification.general_precipitation = True
        days_detailed = self.request.get_all("days_detailed")
        for opt in days_detailed:
            if opt == "temp":
                notification.detailed_temperature = True
            elif opt == "temp_feels":
                notification.detailed_temp_feels_like = True
            elif opt == "wind":
                notification.detailed_wind = True
            elif opt == "uv_index":
                notification.detailed_wind_gusts = True
            elif opt == "humidity":
                notification.detailed_humidity = True
            elif opt == "precipitation":
                notification.detailed_precip = True
            elif opt == "precip_prob":
                notification.detailed_precip_prob = True
        notification.put()
        

app = webapp2.WSGIApplication([
    ('/new', NewNotification),
    ('/add', NotificationAdded)
], debug=True)


def main():
  application.RUN()


if __name__ == '__main__':
  main()
