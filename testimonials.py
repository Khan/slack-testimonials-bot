"""Tool for sending testimonials to slack and responding to slack reactions."""
import datetime
import json
import logging
import re
import urlparse

import alertlib
import humanize
import slackclient

import bot_globals
import webapp_api_client
import secrets

# Channel IDs manually grabbed from
#   https://api.slack.com/methods/channels.list/test
if bot_globals.is_dev_server:
    _MAIN_KA_CHANNEL = "secret-khan-academy"
    _TESTIMONIALS_CHANNEL = "testimonials-test"
    _TESTIMONIALS_CHANNEL_ID = "C0NFLU9UG"
else:
    _MAIN_KA_CHANNEL = "prod-khan-academy"
    _TESTIMONIALS_CHANNEL = "testimonials"
    _TESTIMONIALS_CHANNEL_ID = "C0P49HG5V"

_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"
_TESTIMONIALS_SLACK_BOT_USER_ID = "U0NJ3M8KY"

_NEW_TESTIMONIAL_MESSAGE_PRETEXT = "New testimonial..."
_PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT = "A favorited testimonial..."


class Testimonial(object):
    """Represents a single user's testimonial."""

    def __init__(self, urlsafe_key, date, body, share_allowed, author_name,
            author_email=None):
        self.urlsafe_key = urlsafe_key
        self.date = date
        self.body = body
        self.author_name = author_name or "Anonymous"
        self.author_email = author_email
        self.share_allowed = share_allowed

    @property
    def url(self):
        """URL for editing and publishing this testimonial on /stories."""
        return ("https://www.khanacademy.org/devadmin/stories?key=%s" %
                self.urlsafe_key)

    @staticmethod
    def parse_from_request(request):
        """Parse and return a new Testimonial from incoming request data."""
        return Testimonial(
            request.form['key'],
            datetime.datetime.fromtimestamp(int(request.form['date'])),
            request.form['body'],
            request.form['share_allowed'] == '1',
            request.form.get('author_name', None),  # Author fields optional
            request.form.get('author_email', None)
        )

    @staticmethod
    def fake_instance():
        """Return a fake testimonial for use in testing."""
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
    """Send a slack message on behalf of the testimonials bot.

    Arguments:
        channel: slack channel
        msg: text of main slack message (ignored by slack if attachemnts exist)
        attachments: slack message attachments, which are used for richly-
            formatted messages (see https://api.slack.com/docs/attachments)
    """
    alertlib.Alert(msg).send_to_slack(channel,
            sender=_TESTIMONIALS_SENDER, icon_emoji=_TESTIMONIALS_EMOJI,
            attachments=attachments)


def _slack_api_call(
        method, token=secrets.slack_testimonials_turtle_api_token, **kwargs):
    """Make a slack API call, passing in all kwargs as request data."""
    client = slackclient.SlackClient(token)
    response_json = client.api_call(method, **kwargs)

    try:
        response = json.loads(response_json)
    except:
        # We're forgiving in the case of a slack API failure. We log the
        # failure and return None but don't crash the request.
        logging.error("Failed parsing response for %s API call. Response: %s" %
                (method, response_json))
        return None

    return response


def _sanitize_search_results(match):
    """Cleans up search results.

    - Removes the pretext "New testimonial..."
    - Removes the fields at the bottom for voting/publishing
    - Fixes up the learner's name
    """
    if not 'attachments' in match or len(match['attachments']) == 0:
        return None

    testimonial = match['attachments'][0]
    testimonial['pretext'] = None
    testimonial['fields'] = []

    name = None
    name_match = re.match("\.\.\.from '(\\w*)'", testimonial.get('title', ''))
    if name_match:
        name = name_match.group(1)

    testimonial['title'] = name or "Anonymous"

    return testimonial


# Paramters, subject to change
QUERY_SIZE = 20
MAX_TO_SHOW = 5


def _query_for_channel_name_and_phrases(channel_name, phrases):
    """Send a Slack Search API call for a given channel and list of phrases"""
    query = 'in:"%s" and from:"%s" and %s' % (
            channel_name,
            _TESTIMONIALS_SENDER.lower(),
            ' and '.join(phrases))

    resp = _slack_api_call(
        'search.messages',
        token=secrets.slack_testimonials_search_api_token,
        query=query,
        count=QUERY_SIZE)

    return filter(None,
        map(_sanitize_search_results, resp['messages']['matches']))


def post_search_results(channel_id, search_phrase, requester):
    """Respond to a requester's search phrase in a given channel"""
    testimonials = _query_for_channel_name_and_phrases(
            _MAIN_KA_CHANNEL,
            ['"%s"' % _PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT, search_phrase])

    room_left = MAX_TO_SHOW - len(testimonials)

    if (room_left > 0):
        backup_testimonials = _query_for_channel_name_and_phrases(
                _TESTIMONIALS_CHANNEL,
                ['"%s"' % _NEW_TESTIMONIAL_MESSAGE_PRETEXT, search_phrase])

        # Build a set of title_link's, which can be used to check uniqueness
        # of the testimonials
        title_links = map(lambda t: t.get('title_link', None), testimonials)
        title_link_set = set(filter(None, title_links))

        for testimonial in backup_testimonials[:room_left]:
            if testimonial.get('title_link', '') not in title_link_set:
                testimonials.append(testimonial)
    else:
        testimonials = testimonials[:MAX_TO_SHOW]

    # Modify the first testimonials pretext
    if len(testimonials) > 0:
        testimonials[0]['pretext'] = (
            'Hey @%s, I found %d results for "%s"' % (
                requester, len(testimonials), search_phrase))
        return _send_as_bot(channel_id, "", testimonials)
    else:
        msg = (
            'Hey @%s, no results found for "%s"' % (
                requester, search_phrase))
        return _send_as_bot(channel_id, "", [{'pretext': msg}])


def _create_testimonial_slack_attachments(channel, msg, testimonial):
    """Generate slack attachment data for a richly-formatted announcement.

    Our attachments include calls to action like "[publish this testimonial]"
    or "upvote this to send it to the main #khan-academy room."

    See https://api.slack.com/docs/attachments for more info on formatting
    slack messages with attachments.
    """
    relative_date = humanize.naturaltime(testimonial.date)
    if relative_date == "now":
        relative_date = "just now"

    fields = []
    if channel == _TESTIMONIALS_CHANNEL:
        # If posting in #testimonials, invite people to upvote to share w/ the
        # main #khan-academy channel or, if allowed, to publish on /stories
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

    elif channel == _MAIN_KA_CHANNEL:
        # If posting in main #khan-academy channel, remind people about whether
        # or not they can share the testimonial
        if testimonial.share_allowed:
            fields.append({
                "title": "You're free to share this one!",
                "value": (":newspaper: On twitter, facebook, wherevs - we have"
                          " permission to post this story publicly!"),
                "short": False
            })
        else:
            fields.append({
                "title": "Remember to keep this one internal!",
                "value": (":warning: We weren't given permission to share this"
                          " person's story outside of KA."),
                "short": False
            })

    return [{
        "fallback": ("Testimonial from %s: \"%s\"" %
            (testimonial.author_name, testimonial.body)),
        "pretext": msg,
        "title": ("...from '%s' %s:" %
            (testimonial.author_name, relative_date)),
        "title_link": testimonial.url,
        "text": "\"%s\"" % testimonial.body,
        "color": "#46a8bf",
        "fields": fields
    }]


def _send_testimonial_notification(channel, testimonial):
    """Send notification about a testimonial to one of our target channels.

    If being sent to #testimonials, we're making an announcement about a brand
    new testimonial.

    If being sent to #khan-academy, we're making an announcement about a top/
    favorite testimonial.
    """
    if channel == _TESTIMONIALS_CHANNEL:
        msg = _NEW_TESTIMONIAL_MESSAGE_PRETEXT
    elif channel == _MAIN_KA_CHANNEL:
        msg = _PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT

    attachments = _create_testimonial_slack_attachments(channel, msg,
            testimonial)
    _send_as_bot("#" + channel, msg, attachments)


def _count_upvotes_on_message(slack_message):
    """Return total number of upvotes on slack message.

    All non-downvote emoji reactions are counted as upvotes.
    """
    total = 0
    reactions = slack_message["reactions"]
    for reaction in reactions:
        # Count everything except for downvotes as upvotes
        if reaction["name"] == "-1":
            continue

        count = reaction["count"]

        if _TESTIMONIALS_SLACK_BOT_USER_ID in reaction["users"]:
            # Don't count automatic reactions from the testimonials bot
            count -= 1

        total += count

    return total


def _parse_urlsafe_key_from_message(slack_message):
    """Parse a testimonial's urlsafe_key from testimonal announcement message.

    We use this embedded urlsafe_key in every announcement message as a unique
    testimonial identifier that travels w/ each slack message about the
    testimonial.
    """
    if (not "attachments" in slack_message or
            len(slack_message["attachments"]) == 0):
        return None

    title_link = slack_message["attachments"][0].get("title_link", None)
    parsed_url = urlparse.urlparse(title_link)
    query_dict = urlparse.parse_qs(parsed_url.query)
    vals = query_dict.get("key", [None])

    return vals[0]


def _get_message_from_reaction(reaction_message):
    """Given a slack reaction message, return message it's reacting to."""
    try:
        channel = reaction_message["item"]["channel"]
        ts = reaction_message["item"]["ts"]
    except KeyError:
        logging.error("KeyError when trying to grab channel and ts from %s" %
                reaction_message)
        return None

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
    """Add reaction 'buttons' to a slack message by having bot auto-'react'.

    The bot's reaction emojis will show up as buttons under the message for
    others to click.
    """
    response_thumbs_up = _slack_api_call("reactions.add", name="thumbsup",
            channel=_TESTIMONIALS_CHANNEL_ID, timestamp=slack_message["ts"])

    # TODO(kamens): add back the automatically-added downvote button when we
    # make use of it
    logging.info("Response from reactions.add: %s" % response_thumbs_up)


def _is_specific_testimonial_announcement(slack_message, pretext):
    """Return true if slack msg is a specific testimonial announcement.

    The specific announement type is identified by the message's pretext.
    """
    return (
            slack_message and
            slack_message["type"] == "message" and
            "username" in slack_message and
            slack_message["username"] == _TESTIMONIALS_SENDER and
            len(slack_message["attachments"]) == 1 and
            (slack_message["attachments"][0]["pretext"] == pretext))


def is_new_testimonial_announcement(slack_message):
    """Return true if slack msg is a new testimonial announcement."""
    return _is_specific_testimonial_announcement(slack_message,
            _NEW_TESTIMONIAL_MESSAGE_PRETEXT)


def is_promoted_testimonial_announcement(slack_message):
    """Return true if slack msg is a promoted testimonial announcement."""
    return _is_specific_testimonial_announcement(slack_message,
            _PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT)


def maybe_get_reacted_to_testimonial_message(possible_reaction_message):
    """Return reacted-to slack msg if passed-in msg is a testimonial reaction.

    Only returns the reacted-to slack message if the reaction appears to be on
    a testimonial announcement.

    If the incoming slack message isn't a reaction message or isn't reacting to
    a testimonial announcement, return None.
    """
    if not possible_reaction_message:
        return None

    if not "reaction" in possible_reaction_message:
        return None

    if possible_reaction_message["user"] == _TESTIMONIALS_SLACK_BOT_USER_ID:
        # We ignore the automatic reaction buttons posted by testimonials bot
        return None

    # Get the slack message that this 'reaction message' is a reaction to.
    reacted_to_message = _get_message_from_reaction(possible_reaction_message)

    # Make sure it looks like a testimonial announcement of ours
    if not (is_new_testimonial_announcement(reacted_to_message) or
            is_promoted_testimonial_announcement(reacted_to_message)):
        return None

    return reacted_to_message


def send_updated_reaction_totals(reaction_message, reacted_to_message):
    """Send total emoji vote counts to KA's webapp for recording.

    KA's webapp keeps track of how many emoji reaction votes have been cast on
    each testimonial announcement.
    """
    if reaction_message["reaction"] != "-1":
        upvotes = _count_upvotes_on_message(reacted_to_message)
        urlsafe_key = _parse_urlsafe_key_from_message(reacted_to_message)

        # We treat the message's timestamp as a unique identifier for KA webapp
        message_id = reacted_to_message["ts"]

        webapp_api_client.send_vote_totals(urlsafe_key, upvotes, message_id)


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
