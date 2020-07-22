"""
Dump out the cases data so we can see what is going on in there.
"""
import sys
import os
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
from config import Config

portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD

def connect(layername):
    layer = None
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = FeatureLayer(layername, portal)
    except Exception as e:
        print("Make sure the environment variables are set correctly.")
        sys.exit("Could not connect to portal. \"%s\"" % e)
    return layer

def read_df(layername, fields):
    """
    Read the entire feature layer into a dataframe.

    @Returns
    Dataframe
    """
    layer = connect(layername)
    df = layer.query(out_fields=fields).sdf
    del layer
    return df

if __name__ == "__main__":

    fields = ["utc_date", "editor", "total_cases", "total_negative"]
    df = read_df(Config.COVID_CASES_URL, fields)
    print(df)

