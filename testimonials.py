"""STOPSHIP:docstring"""
import datetime
import logging

import alertlib
import slackclient

import secrets

_TESTIMONIALS_CHANNEL = "#testimonials-test"
# Channel ID grabbed from https://api.slack.com/methods/channels.list/test
_TESTIMONIALS_CHANNEL_ID = "C0NFLU9UG"
_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"

_NEW_TESTIMONIAL_MESSAGE_PRETEXT = "New testimonial received"


class Testimonial(object):
    """STOPSHIP"""
    
    def __init__(self, date, body, author_name, author_email=None):
        """STOPSHIP"""
        self.date = date
        self.body = body
        self.author_name = author_name
        self.author_email = author_email
        # STOPSHIP: add sender_name and perhaps more like 'share_allowed'


def _send_as_bot(msg, attachments):
    """STOPSHIP"""
    alertlib.Alert(msg).send_to_slack(_TESTIMONIALS_CHANNEL,
            sender=_TESTIMONIALS_SENDER, icon_emoji=_TESTIMONIALS_EMOJI,
            attachments=attachments)


def _testimonial_slack_attachments(testimonial):
    """STOPSHIP"""
    return [{
        "fallback": ("New testimonial received from %s: \"%s\"" %
            (testimonial.author_name, testimonial.body)),
        "pretext": _NEW_TESTIMONIAL_MESSAGE_PRETEXT,
        "title": "Testimonial 1234",
        "title_link": "http://khanacademy.org",
        "text": "\"%s\"" % testimonial.body,
        "color": "#46a8bf",
        "fields": [
            {
                "title": "Vote via :thumbsup: or :thumbsdown: below...",
                "value": "...to share this in #khan-academy or hide it,"
                         " respectively.",
                "short": True
            },
            {
                "title": "Or share with our users...",
                "value": "...by [publishing on our /stories page].",
                "short": True
            }
        ]
    }]


def _send_slack_notification(testimonial):
    """STOPSHIP"""
    msg = "New testimonial received"
    attachments = _testimonial_slack_attachments(testimonial)
    _send_as_bot(msg, attachments)


def add_emoji_reaction_buttons(slack_message):
    """STOPSHIP"""
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)

    # STOPSHIP(kamens): doc
    response_thumbs_up = client.api_call("reactions.add", name="thumbsup",
            channel=_TESTIMONIALS_CHANNEL_ID, timestamp=slack_message["ts"])
    response_thumbs_down = client.api_call("reactions.add", name="thumbsdown",
            channel=_TESTIMONIALS_CHANNEL_ID, timestamp=slack_message["ts"])

    logging.info("Responses from reactions.add: (%s) and (%s)" % (
        response_thumbs_up, response_thumbs_down))


def is_new_testimonial_announcement(slack_message):
    """STOPSHIP"""
    return (
            slack_message["type"] == "message" and
            "username" in slack_message and
            slack_message["username"] == _TESTIMONIALS_SENDER and
            len(slack_message["attachments"]) == 1 and
            (slack_message["attachments"][0]["pretext"] ==
                _NEW_TESTIMONIAL_MESSAGE_PRETEXT))


def send_test_msg():
    """STOPSHIP: remove or make unit test"""
    test_testimonial = Testimonial(datetime.datetime.now(),
            "I just scored in the 97th percentile on the GMAT (740/800) and "
            "I owe a HUGE thanks to the Khan Academy. I've never liked math or"
            " had any confidence in my abilities, but I don't come from an "
            "affluent family (no money for my education) and I didn't want to "
            "spend a lot of money on test prep. I ended up spending NOTHING "
            "because the GMAT problem videos and the structured math reviews "
            "were so comprehensive. I started at 1+1=2 and worked my way up "
            "to polynomials. Now I have more confidence in my math skills and "
            "a great GMAT score. Thank you so much!",
            "Sarah")
    _send_slack_notification(test_testimonial)
