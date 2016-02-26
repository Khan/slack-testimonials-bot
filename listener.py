"""Tool for listening to testimonial-related activity in KA's slack channels.

Listener connects to slack's real-time messaging API, keeps an eye on any
activity related to testimonials, and triggers appropriate responses.

For example, listener will notice when a new testimonial notification has been
posted and automatically add an upvote button for others to click by responding
w/ its own emoji reaction.

For another example, listener will notice when an employee has upvoted a
testimonial and send that upvote to KA's API for tracking.

See https://api.slack.com/rtm for more info about slack's real-time API.
"""
import sys
sys.path.append("lib/")  # add third-party libs auto added by app engine

import logging
import time

import slackclient

import secrets
import testimonials


def handle_messages(messages):
    """Handle a list of slack msgs, responding to testimonial-related ones."""
    for message in messages:
        # If we see a new testimonial announcement, automatically add some
        # emoji reaction buttons.
        if testimonials.is_new_testimonial_announcement(message):
            testimonials.add_emoji_reaction_buttons(message)

        # If we see a reaction to a testimonial announcement, respond to it.
        reacted_to_message = (
                testimonials.maybe_get_reacted_to_testimonial_message(message))
        if reacted_to_message:
            testimonials.send_updated_reaction_totals(message,
                    reacted_to_message)


def listen():
    """Start listening to slack channels the Testimonials Turtle bot is in."""
    # STOPSHIP: better error handling so an exception doesn't crash the module
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)
    if not client.rtm_connect():
        logging.critical("Failed to connect to Slack RTM API, bailing.")
        return

    # Once connected, just continually pull messages and handle those that are
    # testimonials-related.
    while True:
        messages = client.rtm_read()
        handle_messages(messages)
        time.sleep(1)


if __name__ == '__main__':
    listen()
