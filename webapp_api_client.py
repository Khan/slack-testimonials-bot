"""Tool for talking to KA's main webapp API."""
import requests


# STOPSHIP: distinguish b/w local and prod servers via app's debug flag
_WEBAPP_URL = "http://localhost:8080"


def _webapp_api_post(relative_url, **kwargs):
    """Send a post to KA's API.
    
    Arguments:
        relative_url: API method being called e.g. /api/internal/stories/update
        **kwargs: dictionary of POST data to be sent
    """
    url = _WEBAPP_URL + relative_url
    return requests.post(url, json=kwargs)


def send_vote_totals(urlsafe_key, upvotes):
    """Send KA API call to update vote totals on a specific testimonial.
    
    Arguments:
        urlsafe_key: testimonial's urlsafe_key (from KA's API)
        upvotes: total # of upvotes on testimonial
    """
    _webapp_api_post("/api/internal/stories/update_votes",
            urlsafe_key=urlsafe_key, upvotes=upvotes)
