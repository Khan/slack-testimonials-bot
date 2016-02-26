"""Tool for talking to KA's main webapp API."""
import logging

import requests

import bot_globals


if bot_globals.is_dev_server:
    _WEBAPP_URL = "http://localhost:8080"
else:
    _WEBAPP_URL = "https://www.khanacademy.org"


def _webapp_api_post(relative_url, **kwargs):
    """Send a post to KA's API.
    
    Arguments:
        relative_url: API method being called e.g. /api/internal/stories/update
        **kwargs: dictionary of POST data to be sent
    """
    url = _WEBAPP_URL + relative_url
    try:
        return requests.post(url, json=kwargs)
    except Exception, e:
        # Gently fail if we ever fail to talk to the KA API: record the error,
        # return None, and let the listener live on.
        logging.error("Failed to send post to KA webapp API: %s" % e)
        return None


def send_vote_totals(urlsafe_key, upvotes, message_id):
    """Send KA API call to update vote totals on a specific testimonial.

    This sends the vote totals coming from a specific slack message. We include
    the message id so the server can properly sum up vote totals if they are
    received from multiple slack messages that refer to the same testimonial.
    
    Arguments:
        urlsafe_key: testimonial's urlsafe_key (from KA's API)
        upvotes: total # of upvotes on testimonial
        message_id: unique-enough identifier of slack message (timestamp)
    """
    _webapp_api_post("/api/internal/stories/update_votes",
            urlsafe_key=urlsafe_key, upvotes=upvotes, message_id=message_id)
