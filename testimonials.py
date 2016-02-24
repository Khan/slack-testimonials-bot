"""STOPSHIP:docstring"""
import datetime
import json
import logging
import urlparse

import alertlib
import humanize
import slackclient

import webapp_api_client
import secrets

# STOPSHIP: use debug flag of some sort to toggle b/w real and fake channels
_MAIN_KA_CHANNEL = "#secret-khan-academy"
_TESTIMONIALS_CHANNEL = "#testimonials-test"
# Channel ID grabbed from https://api.slack.com/methods/channels.list/test
_TESTIMONIALS_CHANNEL_ID = "C0NFLU9UG"

_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"
_TESTIMONIALS_SLACK_BOT_USER_ID = "U0NJ3M8KY"

# STOPSHIP: better pretexts
_NEW_TESTIMONIAL_MESSAGE_PRETEXT = "New testimonial..."
_PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT = "Favorite testimonial"


class Testimonial(object):
    """STOPSHIP"""

    def __init__(self, urlsafe_key, date, body, share_allowed, author_name,
            author_email=None):
        """STOPSHIP"""
        self.urlsafe_key = urlsafe_key
        self.date = date
        self.body = body
        self.author_name = author_name
        self.author_email = author_email
        self.share_allowed = share_allowed

    @property
    def url(self):
        """STOPSHIP"""
        return ("https://www.khanacademy.org/devadmin/stories?key=%s" %
                self.urlsafe_key)

    @staticmethod
    def parse_from_request(request):
        """STOPSHIP"""
        return Testimonial(
            request.form['key'],
            datetime.datetime.fromtimestamp(int(request.form['date'])),
            request.form['body'],
            request.form['share_allowed'] == '1',
            request.form['author_name'],
            request.form['author_email']
        )

    @staticmethod
    def fake_instance():
        return Testimonial(
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
            "a great GMAT score.\n\n\nThank you so much!",
            False,
            "Sarah")


def _send_as_bot(channel, msg, attachments):
    """STOPSHIP"""
    alertlib.Alert(msg).send_to_slack(channel,
            sender=_TESTIMONIALS_SENDER, icon_emoji=_TESTIMONIALS_EMOJI,
            attachments=attachments)


def _slack_api_call(method, **kwargs):
    """STOPSHIP"""
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)

    response_json = client.api_call(method, **kwargs)

    try:
        response = json.loads(response_json)
    except:
        # STOPSHIP: doc about being forgiving
        logging.error("Failed parsing response for %s API call. Response: %s" %
                (method, response_json))
        return None

    return response


def _create_testimonial_slack_attachments(channel, msg, testimonial):
    """STOPSHIP"""
    author_text = testimonial.author_name
    if testimonial.author_email:
        author_text = ("<mailto:%s|%s>" %
                (testimonial.author_email, testimonial.author_name))

    relative_date = humanize.naturaltime(testimonial.date)
    if relative_date == "now":
        relative_date = "just now"

    fields = []
    if channel == _TESTIMONIALS_CHANNEL:
        fields.append({
            "title": "Share w/ the team internally...",
            "value": "Voting your :thumbsup: will send this to #khan-academy.",
                    "short": True
        })

        if testimonial.share_allowed:
            fields.append({
                "title": "...or share w/ our users.",
                "value": ("By <%s|publishing on our stories page>." %
                    testimonial.url),
                "short": True
            })
        else:
            fields.append({
                "title": "...but remember to keep this one internal!",
                "value": (":warning: We don't have permission to share outside"
                          " KA."),
                "short": True
            })

    return [{
        "fallback": ("Testimonial from %s: \"%s\"" %
            (testimonial.author_name, testimonial.body)),
        "pretext": msg,
        "title": ("...from '%s' %s:" %
            (author_text, relative_date)),
        "title_link": testimonial.url,
        "text": "\"%s\"" % testimonial.body,
        "color": "#46a8bf",
        "fields": fields
    }]


def _send_testimonial_notification(channel, testimonial):
    """STOPSHIP"""
    if channel == _TESTIMONIALS_CHANNEL:
        msg = _NEW_TESTIMONIAL_MESSAGE_PRETEXT
    elif channel == _MAIN_KA_CHANNEL:
        msg = _PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT

    attachments = _create_testimonial_slack_attachments(channel, msg,
            testimonial)
    _send_as_bot(channel, msg, attachments)


def _count_upvotes_on_message(slack_message):
    """STOPSHIP"""
    total = 0
    reactions = slack_message["reactions"]
    for reaction in reactions:
        # Count everything except for downvotes as upvotes
        if reaction["name"] != "-1":
            total += reaction["count"]
    return total


def _parse_urlsafe_key_from_message(slack_message):
    """STOPSHIP"""
    if (not "attachments" in slack_message or
            len(slack_message["attachments"]) == 0):
        return None

    title_link = slack_message["attachments"][0].get("title_link", None)
    parsed_url = urlparse.urlparse(title_link)
    query_dict = urlparse.parse_qs(parsed_url.query)
    vals = query_dict.get("key", [None])

    return vals[0]


def _get_message_from_reaction(reaction_message):
    """STOPSHIP"""
    try:
        channel = reaction_message["item"]["channel"]
        ts = reaction_message["item"]["ts"]
    except KeyError:
        logging.error("KeyError when trying to grab channel and ts from %s" %
                reaction_message)
        return None

    # STOPSHIP: caching

    response = _slack_api_call("channels.history", channel=channel,
            latest=ts, oldest=ts, inclusive=1, count=1)

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
    # STOPSHIP(kamens): doc
    response_thumbs_up = _slack_api_call("reactions.add", name="thumbsup",
            channel=_TESTIMONIALS_CHANNEL_ID, timestamp=slack_message["ts"])

    # TODO(kamens): add back the automatically-added downvote button when we
    # make use of it
    logging.info("Response from reactions.add: %s" % response_thumbs_up)


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


def is_reaction_to_testimonial(reaction_message):
    """STOPSHIP"""
    if not reaction_message:
        return False

    if not "reaction" in reaction_message:
        return False

    if reaction_message["user"] == _TESTIMONIALS_SLACK_BOT_USER_ID:
        # We ignore the automatic reaction buttons posted by testimonials bot
        return False

    reacted_to_message = _get_message_from_reaction(reaction_message)

    # STOPSHIP: make this work for both 'new' and 'promoted' announcements
    return is_new_testimonial_announcement(reacted_to_message)


def send_updated_reaction_totals(reaction_message):
    """STOPSHIP"""
    if reaction_message["reaction"] != "-1":
        reacted_to_message = _get_message_from_reaction(reaction_message)

        upvotes = _count_upvotes_on_message(reacted_to_message)
        urlsafe_key = _parse_urlsafe_key_from_message(reacted_to_message)

        webapp_api_client.send_vote_totals(urlsafe_key, upvotes)


def notify_testimonials_channel(testimonial):
    """Sends slack notification alerting #testimonials about a new testimonial.

    Invoked from /api/new_testimonial, which is hit upon submitting a
    testimonial on khanacademy.org/stories or via forwarding an email to
    testimonials_turtle@khan-academy.appspotmail.com
    """
    _send_testimonial_notification(_TESTIMONIALS_CHANNEL, testimonial)


def promote_to_main_channel(testimonial):
    """Sends an upvoted slack notification to main #khan-academy channel.

    This only happens once somebody has upvoted a testimonial in the
    #testimonials room. The main KA webapp will hit /api/promote_testimonial
    in that case, which triggers this promote-to-main-slack-channel process.
    """
    _send_testimonial_notification(_MAIN_KA_CHANNEL, testimonial)
