# Note this will not override existing environment settings
from dotenv import load_dotenv
load_dotenv()

import os
class Config(object):
    """ Read environment here to create configuration data. """
    SECRET_KEY=os.environ.get('SECRET_KEY') or "12345678"

    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')

    COVID_CASES_URL = os.environ.get('COVID_CASES_URL')
    PPE_INVENTORY_URL = os.environ.get('PPE_INVENTORY_URL')
   
    pass

if __name__ == "__main__":

    # To test this in VSCODE
    # source ~/.conda/envs/covid/etc/conda/activate.d/env_vars.sh

    assert Config.SECRET_KEY

    assert Config.PORTAL_URL
    assert Config.PORTAL_USER
    assert Config.PORTAL_PASSWORD
    
    assert Config.COVID_CASES_URL
    assert Config.PPE_INVENTORY_URL

    pass

# That's all!
