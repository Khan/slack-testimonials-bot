"""STOPSHIP:docstring"""
import flask

import testimonials


app = flask.Flask(__name__)


@app.route('/testsend')
def test_send():
    testimonials.send_test_msg()
    return 'OK'


if __name__ == '__main__':
    # STOPSHIP: turn off debug in prod
    app.run(host='127.0.0.1', port=8080, debug=True)
