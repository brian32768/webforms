from logging import DEBUG
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """ 
Load configuration from environment. 

In PRODUCTION conda sets up the environment,
so look in ~/.conda/envs/covid/etc/conda/activate.d/env_vars.sh
to see how it is set up. 
    """
    SECRET_KEY=os.environ.get('SECRET_KEY', "8765431012345678")

    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')

    COVID_CASES_URL   = "https://delta.co.clatsop.or.us/server/rest/services/COVID19/covid19_cases/FeatureServer/0"
    PUBLIC_WEEKLY_URL = "https://delta.co.clatsop.or.us/server/rest/services/covid19_public_weekly_data/FeatureServer/0"
    PPE_INVENTORY_URL = "https://delta.co.clatsop.or.us/server/rest/services/COVID19/covid19_ppe_inventory/FeatureServer/0"

    COVID_DAILY_CASES_URL = "https://services8.arcgis.com/l89P2qlKPxgrFDLw/arcgis/rest/services/covid_cases_current_day/FeatureServer/0"

    pass

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG = True # Loglevel

class TestConfig(Config):
    TESTING = True
    DEBUG = True # Loglevel

class ProdConfig(Config):
    DEBUG = False # Loglevel


config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
    'default': ProdConfig
}

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
