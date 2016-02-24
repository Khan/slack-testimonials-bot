"""STOPSHIP:docstring"""
import flask
from flask import request

import testimonials


app = flask.Flask(__name__)


# TODO(kamens): separate below hacky tests into unit tests
@app.route('/test_new_testimonial')
def test_new_testimonial():
    """STOPSHIP"""
    testimonial = testimonials.Testimonial.fake_instance()

    # Allow overriding the share_allowed bit for testing display of
    # share-allowed and -disabled formatting
    testimonial.share_allowed = request.args.get("share_allowed", None) == '1'

    testimonials.notify_testimonials_channel(testimonial)
    return 'OK'


@app.route('/test_promote_testimonial')
def test_promote_testimonial():
    """STOPSHIP"""
    testimonial = testimonials.Testimonial.fake_instance()
    testimonials.promote_to_main_channel(testimonial)
    return 'OK'


@app.route('/api/new_testimonial', methods=['POST'])
def new_testimonial():
    """STOPSHIP"""
    testimonial = testimonials.Testimonial.parse_from_request(request)
    testimonials.notify_testimonials_channel(testimonial)
    return 'OK'


@app.route('/api/promote_testimonial', methods=['POST'])
def promote_testimonial():
    """STOPSHIP"""
    testimonial = testimonials.Testimonial.parse_from_request(request)
    testimonials.promote_to_main_channel(testimonial)
    return 'OK'


if __name__ == '__main__':
    # STOPSHIP: turn off debug in prod
    app.run(host='127.0.0.1', port=8081, debug=True)
