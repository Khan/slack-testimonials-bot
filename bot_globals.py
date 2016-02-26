"""Global vars set at startup."""
import os

# STOPSHIP: figure out how to toggle this when starting listener
is_dev_server = (os.environ.get("SERVER_SOFTWARE", "Development")
                 .startswith('Development'))
