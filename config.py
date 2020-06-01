# Note this will not override existing environment settings
from dotenv import load_dotenv
load_dotenv()

import os
class Config(object):
    """ Read environment here to create configuration data. """
    SECRET_KEY=os.environ.get('NO_TIME_LIKE_THE_present') or "12345678"

    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_FEATURE_LAYER = os.environ.get('PORTAL_FEATURE_LAYER')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')
    pass

# That's all!
