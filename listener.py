"""STOPSHIP"""
import logging
import time

import slackclient

import secrets
import testimonials


def handle_messages(messages):
    """STOPSHIP"""
    # STOPSHIP: change logging to appropriate levels
    for message in messages:
        if testimonials.is_new_testimonial_announcement(message):
            logging.critical("Found new testimonial message: %s" % message)
            testimonials.add_emoji_reaction_buttons(message)
        elif testimonials.is_reaction_to_testimonial(message):
            logging.critical("Found reaction to testimonial: %s" % message)
            testimonials.send_updated_reaction_totals(message)
        else:
            logging.critical("Ignoring: %s" % message)


def listen():
    """STOPSHIP"""
    # STOPSHIP: better error handling so an exception doesn't crash the module
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)
    if not client.rtm_connect():
        logging.critical("Failed to connect to Slack RTM API, bailing.")
        return

    # STOPSHIP: explanation
    while True:
        messages = client.rtm_read()
        handle_messages(messages)
        time.sleep(1)


if __name__ == '__main__':
    listen()
