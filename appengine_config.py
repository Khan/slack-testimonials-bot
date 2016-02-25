import os

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

# Work around dev environment's required SSL hack. Needed to be able to import
# our python slack client lib. See http://stackoverflow.com/q/16192916/893652
# and https://blog.bekt.net/p/gae-ssl/
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']
