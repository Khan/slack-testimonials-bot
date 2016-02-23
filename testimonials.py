"""STOPSHIP:docstring"""
import alertlib

_TESTIMONIALS_CHANNEL = "#testimonials-test"
_TESTIMONIALS_SENDER = "Testimonials Turtle"
_TESTIMONIALS_EMOJI = ":turtle:"


def send_as_bot(msg):
    alertlib.Alert(msg).send_to_slack(_TESTIMONIALS_CHANNEL,
            sender=_TESTIMONIALS_SENDER, icon_emoji=_TESTIMONIALS_EMOJI)


def send_test_msg():
    send_as_bot("Monkeys! STOPSHIP")
