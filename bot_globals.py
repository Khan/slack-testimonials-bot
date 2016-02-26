"""Global vars set at startup."""
import os
import sys

if len(sys.argv) > 0 and sys.argv[0] == "listener.py":
    # If we're running the listener, check if we're running in dev mode
    # TODO(kamens): this is crude argument parsing logic, if this gets extended
    # we should use argparse
    is_dev_server = len(sys.argv) < 2 or sys.argv[1] != "--prod"
else:
    # If we're running app engine, check if we're running on dev server
    is_dev_server = (
            os.environ.get("SERVER_SOFTWARE", "Development").startswith(
                "Development"))
