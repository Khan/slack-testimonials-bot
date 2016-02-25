"""Global vars set at startup."""
import os

is_dev_server = (os.environ.get("SERVER_SOFTWARE", "Development")
                 .startswith('Development'))
