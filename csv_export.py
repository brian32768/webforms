#!/usr/bin/env -S conda run -n covid python
"""
    Using a dataframe, 
    Calculate values for the 7-day moving window average.
    Export it as a csv file so D3 in JavaScript can read it.

    This can be run as a standalone script to test it,
    but normally the csv_exporter is called from webforms.
    When running standalone it will need a proper configuration
    to be able to read the data from Delta.
"""
import os
import pytz
from arcgis.gis import GIS
import pandas as pd
import numpy as np
import csv
from datetime import datetime, timezone, timedelta

from utils import connect

# Ignore data more than 6 months old
DAYS = 30 * 6

tformat = "%Y-%m-%d %H:%M"
pactz = pytz.timezone('America/Los_Angeles')

def utc2localdate(utc_naive):
    """ input: timestamp from dataframe in utc, "YYYY-MM-DD HH:MM:SS"
        output: string in local time, same format """

    # I'm not sure but maybe I should just set tzinfo here too??
    # tzinfo = timezone.utc
    #return t.astimezone(timezone.utc).replace(microsecond=0, second=0)
    utc = utc_naive.tz_localize(timezone.utc)
    #print('utc=', utc, type(utc))
    # We're only interested in the date
    p = utc.astimezone(pactz).date()
    rval = p.strftime('%m/%d/%y')
    return rval

def clean_data(sdf, days):
    """ Return two df's, one for total cases and one for daily cases. """

    # There should be about 100 rows here,
    # because it's already been filtered for EMD entries only.
    print(len(sdf), sdf.columns)

    # Get rid of extra readings (just one a day is good)
    # With EMD data, these are just test cases when I was developing webforms
    #df = sdf.drop_duplicates(subset='date')
#    print(len(local_df), len(df))

    # Get rid of everything but the time and count.
    #keepers = ['utc_date', 'total_cases']
    #dedupe = df.filter(items=keepers)

    # Get ready to calc daily_cases    
    #sorted = dedupe.set_index('utc_date')

    # save the total cases so we can add it back in
    #total_cases = sorted['total_cases']
    #
    ## Calculate proper value for daily_cases
    #dailydf = sorted.diff()
    #rdf = dailydf.rename(columns={'total_cases':'new_cases'})
    #
    # put total_cases back in
    #rdf['total_cases'] = total_cases

    # Convert to localtime
    # see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    date = []
    for utc_naive in sdf.loc[:, 'utc_date']:
        date.append(utc2localdate(utc_naive))
    sdf['date'] = date

    if days > 0:
        start_date = datetime.utcnow() - timedelta(days)
        df = sdf[sdf['last_update'] >= start_date].set_index('date')
    else:
        df = sdf.set_index('date')

    # Get rid of everything but the time and count.
    keepers = ['date', 'new_cases']
    daily_df = df.filter(items=keepers)
    daily_df.rename(columns={'new_cases':'cases'},inplace=True)

    # Calculate a 7 day average, some day...
    daily_df['avg'] = daily_df.iloc[:,0].rolling(window=7).mean()

    # Get rid of everything but the time and count.
    keepers = ['date', 'total_cases']
    total_df = df.filter(items=keepers)
    total_df.rename(columns={'total_cases':'cases'},inplace=True)

    # Calculate a 7 day average, some day...
    total_df['avg'] = total_df.iloc[:,0].rolling(window=7).mean()

    return (daily_df, total_df)

def csv_exporter(df, outputdir):
    """ NB This is called from the webforms app. """

    (daily_df, total_df) = clean_data(df, DAYS)

    # Easy peasy once the data is in a DF.

#    print(daily_df)
#    print(total_df)

    daily_df.to_csv(os.path.join(outputdir, 'emd_daily_cases.csv'), header=True, index=True)
    total_df.to_csv(os.path.join(outputdir, 'emd_total_cases.csv'), header=True, index=True)
        
    return True

#============================================================================
if __name__ == "__main__":

    from config import config

    configObj = config['testing']
    
    # read data from here
    portalUrl       = configObj.PORTAL_URL
    portalUser      = configObj.PORTAL_USER
    portalPasswd    = configObj.PORTAL_PASSWORD
    featurelayerUrl = configObj.COVID_CASES_URL

    # fail immediately if the environment is not set up correctly
    assert portalUrl
    assert portalUser
    assert portalPasswd
    assert featurelayerUrl

    # For testing, try to write to where the D3 JavaScript lives
    outputdir = '../corona_collector/src'
    if not os.path.exists(outputdir):
        # whelp write locally then
        outputdir = '.'

    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, featurelayerUrl)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    sdf = pd.DataFrame.spatial.from_layer(layer)

    # We're only interested in data manually entered for Clatsop
    print(len(sdf))
    sdf = sdf[sdf.editor == 'EMD']

    csv_exporter(sdf, outputdir)
    print("...and we're done")
    exit(0)
