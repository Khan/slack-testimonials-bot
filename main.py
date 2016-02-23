"""STOPSHIP:docstring"""
import webapp2

import testimonials


class TestSend(webapp2.RequestHandler):
    def get(self):
        testimonials.send_test_msg()


app = webapp2.WSGIApplication([
    ('/testsend', TestSend),
])
