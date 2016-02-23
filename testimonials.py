"""STOPSHIP:docstring"""
import datetime
import json
import logging

import alertlib
import humanize
import slackclient

import secrets

_TESTIMONIALS_CHANNEL = "#testimonials-test"
# Channel ID grabbed from https://api.slack.com/methods/channels.list/test
_TESTIMONIALS_CHANNEL_ID = "C0NFLU9UG"
_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"
_TESTIMONIALS_SLACK_BOT_USER_ID = "U0NJ3M8KY"

_NEW_TESTIMONIAL_MESSAGE_PRETEXT = "New testimonial received"


class Testimonial(object):
    """STOPSHIP"""
    
    def __init__(self, urlsafe_key, date, body, author_name,
            author_email=None):
        """STOPSHIP"""
        self.urlsafe_key = urlsafe_key
        self.date = date
        self.body = body
        self.author_name = author_name
        self.author_email = author_email
        # STOPSHIP: add sender_name and perhaps more like 'share_allowed'

    @property
    def url(self):
        return ("https://www.khanacademy.org/devadmin/stories/%s" %
                self.urlsafe_key)


def _send_as_bot(msg, attachments):
    """STOPSHIP"""
    alertlib.Alert(msg).send_to_slack(_TESTIMONIALS_CHANNEL,
            sender=_TESTIMONIALS_SENDER, icon_emoji=_TESTIMONIALS_EMOJI,
            attachments=attachments)


def _testimonial_slack_attachments(testimonial):
    """STOPSHIP"""
    author_text = testimonial.author_name
    if testimonial.author_email:
        author_text = ("<mailto:%s|%s>" %
                (testimonial.author_email, testimonial.author_name))

    relative_date = humanize.naturaltime(testimonial.date)
    if relative_date == "now":
        relative_date = "just now"

    return [{
        "fallback": ("New testimonial received from %s: \"%s\"" %
            (testimonial.author_name, testimonial.body)),
        "pretext": _NEW_TESTIMONIAL_MESSAGE_PRETEXT,
        "title": ("From '%s' %s..." %
            (author_text, relative_date)),
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
                "value": ("...by <%s|publishing on our stories page>" %
                    testimonial.url),
                "short": True
            }
        ]
    }]


def _send_slack_notification(testimonial):
    """STOPSHIP"""
    msg = "New testimonial received"
    attachments = _testimonial_slack_attachments(testimonial)
    _send_as_bot(msg, attachments)


def _get_message_from_timestamp(channel, ts):
    """STOPSHIP"""
    # STOPSHIP: caching
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)

    response_json = client.api_call("channels.history", channel=channel,
            latest=ts, oldest=ts, inclusive=1, count=1)

    try:
        response = json.loads(response_json)
    except:
        logging.error("Failed parsing response when searching for message %s "
                "in channel %s. Response: %s" % (ts, channel, response_json))

    if (not response or 
            response["ok"] != True or
            len(response["messages"]) != 1):
        logging.error(
                "Unable to find message %s in channel %s. Response: '%s'" %
                (ts, channel, response))
        return None

    # Found message in channel!
    return response["messages"][0]


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
            slack_message and
            slack_message["type"] == "message" and
            "username" in slack_message and
            slack_message["username"] == _TESTIMONIALS_SENDER and
            len(slack_message["attachments"]) == 1 and
            (slack_message["attachments"][0]["pretext"] ==
                _NEW_TESTIMONIAL_MESSAGE_PRETEXT))


def is_reaction_to_testimonial(slack_message):
    """STOPSHIP"""
    if not slack_message:
        return False

    if not "reaction" in slack_message:
        return False

    if slack_message["user"] == _TESTIMONIALS_SLACK_BOT_USER_ID:
        # We ignore the automatic reaction buttons posted by testimonials bot
        return False

    reacted_to_message = _get_message_from_timestamp(
            slack_message["item"]["channel"], slack_message["item"]["ts"])

    # STOPSHIP: make this work for both 'new' and 'promoted' announcements
    return is_new_testimonial_announcement(reacted_to_message)


def respond_to_reaction(slack_message):
    """STOPSHIP"""
    pass


def send_test_msg():
    """STOPSHIP: remove or make unit test"""
    test_testimonial = Testimonial(
            "fakeurlkey",
            datetime.datetime.now(),
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
