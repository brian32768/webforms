# 
#  Load the case data for Clatsop County
#  into data frames
# 
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import arcgis.features
import pytz
from datetime import datetime, timezone, timedelta
from config import Config

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
    return utc.astimezone(pactz).date()
    #rval = p.strftime('%m/%d/%y')
    #return p

def connect(layername):
    layer = None
    portal = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    #print("Logged in as " + str(portal.properties.user.username))
    layer = FeatureLayer(layername, portal)
    return layer

def read_df():
    layer = connect(Config.COVID_CASES_URL)
    sdf = pd.DataFrame.spatial.from_layer(layer)
    del layer
    df = sdf[sdf.editor == 'EMD'] # Just Clatsop County
    #print(df)
    return df

def clean_data(sdf, days):
    """ Return two df's, one for total cases and one for daily cases. """

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
    total_df.reset_index()

    return (daily_df.reset_index(), total_df.reset_index())

def read_cases(days):
    sdf = read_df()
    return clean_data(sdf, days)

# ==================================================================================

if __name__ == "__main__":
    
    days = 6 * 7

    (daily_df, total_df) = read_cases(days)
    assert len(daily_df)>0
    assert len(total_df)>0

    print(daily_df)
    print(total_df)

# That's all!
