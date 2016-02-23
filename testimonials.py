"""STOPSHIP:docstring"""
import datetime

import alertlib

_TESTIMONIALS_CHANNEL = "#testimonials-test"
_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"


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
        "pretext": "New testimonial received",
        "title": "Testimonial 1234",
        "title_link": "http://khanacademy.org",
        "text": "\"%s\"" % testimonial.body,
        "color": "#46a8bf",
        "fields": [
            {
                "title": "Vote up or down",
                "value": "...to share in main room",
                "short": True
            },
            {
                "title": "Publish to /stories",
                "value": "[by clicking here]",
                "short": True
            }
        ]
    }]


def _send_slack_notification(testimonial):
    """STOPSHIP"""
    msg = "New testimonial received"
    attachments = _testimonial_slack_attachments(testimonial)
    _send_as_bot(msg, attachments)


def send_test_msg():
    """STOPSHIP: remove or make unit test"""
    test_testimonial = Testimonial(datetime.datetime.now(),
            """I just scored in the 97th percentile on the GMAT (740/800) and I
            owe a HUGE thanks to the Khan Academy. I've never liked math or had
            any confidence in my abilities, but I don't come from an affluent
            family (no money for my education) and I didn't want to spend a lot
            of money on test prep. I ended up spending NOTHING because the GMAT
            problem videos and the structured math reviews were so
            comprehensive. I started at 1+1=2 and worked my way up to
            polynomials. Now I have more confidence in my math skills and a
            great GMAT score. Thank you so much!""",
            "Sarah")
    _send_slack_notification(test_testimonial)
