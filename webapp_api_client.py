"""STOPSHIP"""
import requests


# STOPSHIP: distinguish b/w local and prod servers via app's debug flag
_WEBAPP_URL = "http://localhost:8080"


def _webapp_api_post(relative_url, **kwargs):
    """STOPSHIP"""
    url = _WEBAPP_URL + relative_url
    return requests.post(url, data=kwargs)


def send_vote_totals(urlsafe_key, upvotes):
    """STOPSHIP"""
    _webapp_api_post("/api/internal/stories/update_votes",
            urlsafe_key=urlsafe_key, upvotes=upvotes)
