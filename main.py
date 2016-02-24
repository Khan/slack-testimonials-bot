"""STOPSHIP:docstring"""
import datetime
import flask
from flask import request

import testimonials


app = flask.Flask(__name__)


@app.route('/testsend')
def test_send():
    testimonials.send_test_msg()
    return 'OK'


@app.route('/notify', methods=['POST'])
def notify():
    key = request.form['key']
    date = datetime.datetime.fromtimestamp(int(request.form['date']))
    body = request.form['body']
    author_name = request.form['author_name']
    author_email = request.form['author_email']

    testimonials.send_msg(key, date, body, author_name, author_email)
    return 'OK'


if __name__ == '__main__':
    # STOPSHIP: turn off debug in prod
    app.run(host='127.0.0.1', port=8081, debug=True)
