# Note this will not override existing environment settings
from dotenv import load_dotenv
load_dotenv()

import os
class Config(object):
    """ Read environment here to create configuration data. """
    SECRET_KEY=os.environ.get('NO_TIME_LIKE_THE_present') or "12345678"

    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')

    CASES_LAYER = os.environ.get('CASES_LAYER')
    CASES_TITLE = os.environ.get('CASES_TITLE')
    PPE_LAYER   = os.environ.get('PPE_LAYER')
    PPE_TITLE   = os.environ.get('PPE_TITLE')

    pass

# That's all!
