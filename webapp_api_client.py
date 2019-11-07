"""Tool for talking to KA's main webapp API."""
import logging

import json
import urllib2

import bot_globals
import secrets


if bot_globals.is_dev_server:
    # Send the query directly to the graphql-gateway in dev.
    # TODO(dhruv): make this localhost:8081 once we have nginx doing dispatch
    # to graphql-gateway correctly.
    # TODO(dhruv): read port values from PORTS.yaml instead of hard coding.
    _WEBAPP_URL = "http://localhost:8102"
else:
    _WEBAPP_URL = "https://www.khanacademy.org"

UPDATE_VOTES_MUTATION = """
    mutation updateVotes(
      $storyKey:ID!,
      $votes:Int!,
      $messageKey:String!,
      $secretKey: String!
    ) {
      updateStoryVoteCount (
        storyKey: $storyKey,
        votes: $votes,
        messageKey: $messageKey,
        secretKey:$secretKey
      ) {
        success
      }
    }
"""


def _webapp_graphql_mutation(mutation, variables):
    """Send a graphql mutation request to KA

    Arguments:
        mutation: the string that represents the mutation to be done, for
            example: '{ doFoo(bar: $baz) {success} }'
        variables: a dictionary of variables included in the mutation to pass
            along to the graphql endpoint.
    """
    # We send all requests directly to the graphql-gateway
    url = _WEBAPP_URL + "/graphql/updateVotes"
    data = json.dumps({
        'query': mutation,
        'variables': variables,
    })
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})

    try:
        urllib2.urlopen(req)
    except Exception, e:
        # Gently fail if we ever fail to talk to the KA API: record the error,
        # return None, and let the listener live on.
        logging.error("Failed to send post to KA webapp API: %s" % e)


def send_vote_totals(urlsafe_key, upvotes, message_id):
    """Send KA API call to update vote totals on a specific testimonial.

    This sends the vote totals coming from a specific slack message. We include
    the message id so the server can properly sum up vote totals if they are
    received from multiple slack messages that refer to the same testimonial.

    Arguments:
        urlsafe_key: testimonial's urlsafe_key (from KA's API)
        upvotes: total # of upvotes on testimonial
        message_id: unique-enough identifier of slack message (timestamp)
    """
    variables = {
        "storyKey": urlsafe_key,
        "votes": upvotes,
        "messageKey": message_id,
        "secretKey": secrets.user_story_upvoting_secret
    }

    _webapp_graphql_mutation(UPDATE_VOTES_MUTATION, variables)
