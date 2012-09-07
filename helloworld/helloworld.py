from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import os

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
    application.run()

if __name__ == "__main__":
    main()
