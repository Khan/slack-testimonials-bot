"""STOPSHIP"""
import logging
import time

import slackclient

import secrets


def listen():
    """STOPSHIP"""
    client = slackclient.SlackClient(
            secrets.slack_testimonials_turtle_api_token)
    if not client.rtm_connect():
        logging.critical("Failed to connect to Slack RTM API, bailing.")
        return

    # STOPSHIP: explanation
    while True:
        messages = client.rtm_read()
        logging.critical(messages)
        time.sleep(1)


if __name__ == '__main__':
    listen()
