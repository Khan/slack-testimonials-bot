"""Web service that handles webhooks related to our testimonial slack bot.

Used to trigger notifications in slack when new testimonials arrive, to send
testimonial emoji reaction information to KA's webapp server (the source of
truth for all testimonials), and to promote favorite testimonials to slack
channels where all employees hang out and will be inspired ;).
"""
import flask
from flask import request

import testimonials


app = flask.Flask(__name__)


def _get_fake_testimonial():
    """Return a fake testimonial for use in hacky manual testing."""
    testimonial = testimonials.Testimonial.fake_instance()

    # Allow overriding the share_allowed bit for testing display of
    # share-allowed and -disabled formatting
    testimonial.share_allowed = request.args.get("share_allowed", None) == '1'

    return testimonial


# TODO(kamens): separate below hacky tests into unit tests
@app.route('/test_new_testimonial')
def test_new_testimonial():
    """Test sending notification about a new fake testimonial."""
    testimonials.notify_testimonials_channel(_get_fake_testimonial())
    return 'OK'


@app.route('/test_promote_testimonial')
def test_promote_testimonial():
    """Test sending promoted notification about a favorite fake testimonial."""
    testimonials.promote_to_main_channel(_get_fake_testimonial())
    return 'OK'


@app.route('/api/new_testimonial', methods=['POST'])
def new_testimonial():
    """Send notification about a newly created testimonial.

    This webhook is hit by the main KA webapp whenever a new testimonial is
    received.
    """
    testimonial = testimonials.Testimonial.parse_from_request(request)
    testimonials.notify_testimonials_channel(testimonial)
    return 'OK'


@app.route('/api/promote_testimonial', methods=['POST'])
def promote_testimonial():
    """Send a 'promoted' testimonial notification (to KA's main slack channel).

    This webhook is hit by the main KA webapp when it notices that a
    testimonial has received a certain number of upvotes in the #testimonials
    channel.
    """
    testimonial = testimonials.Testimonial.parse_from_request(request)
    testimonials.promote_to_main_channel(testimonial)
    return 'OK'


@app.route('/api/testimonial_search', methods=['POST'])
def test_fetch_testimonial():
    """Test sending promoted notification about a favorite fake testimonial."""
    channel_id = request.form['channel_id']
    search_phrase = request.form['text']
    requester = request.form['user_name']

    testimonials.post_search_results(channel_id, search_phrase, requester)

    return 'OK'
