import json
import sys
import unittest.mock
import unittest

sys.modules['secrets'] = unittest.mock.Mock()

import testimonials


class TestTestimonials(unittest.TestCase):
    def test_search(self):
        """Tests the search functionality of the slack bot"""
        channel = "my-fancy-channel"
        search_phrase = "abcdef"
        requester = "sarah"

        NO_RESULTS_QUERY = "ACDEFGHIJKL"

        def _mock_send_as_bot(channel, msg, attachments):
            return {
                'channel': channel,
                'msg': msg,
                'attachments': attachments,
            }

        def _mock_slack_api_call(method, token, **kwargs):
            json_data = "{}"
            if NO_RESULTS_QUERY in kwargs['query']:
                json_data = open('fixtures/no-results-search.json').read()

            elif testimonials._MAIN_KA_CHANNEL in kwargs['query']:
                self.assertIn(
                    testimonials._PROMOTED_TESTIMONIAL_MESSAGE_PRETEXT,
                    kwargs['query'])

                json_data = open('fixtures/primary-room-search.json').read()
            elif testimonials._TESTIMONIALS_CHANNEL in kwargs['query']:
                self.assertIn(
                    testimonials._NEW_TESTIMONIAL_MESSAGE_PRETEXT,
                    kwargs['query'])

                json_data = open('fixtures/secondary-room-search.json').read()

            return json.loads(json_data)

        testimonials._send_as_bot = _mock_send_as_bot
        testimonials._slack_api_call = _mock_slack_api_call

        message = testimonials.post_search_results(
            channel, search_phrase, requester)

        message_header = message['attachments'][0]['pretext']

        self.assertEqual(message['channel'], channel)
        self.assertEqual(5, len(message['attachments']))

        self.assertIn("@%s" % requester, message_header)
        self.assertIn(search_phrase, message_header)
        self.assertIn("5", message_header)

        # A search with no results
        message = testimonials.post_search_results(
            channel, NO_RESULTS_QUERY, requester)

        message_header = message['attachments'][0]['pretext']

        self.assertEqual(message['channel'], channel)

        self.assertIn("@%s" % requester, message_header)
        self.assertIn("no results found", message_header)


if __name__ == '__main__':
    unittest.main()
