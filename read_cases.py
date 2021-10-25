# 
#  Load the case data for Clatsop County
#  into data frames
# 
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer, Table
import arcgis.features
import pytz
from datetime import datetime, timezone, timedelta
from config import Config

tformat = "%Y-%m-%d %H:%M"
pactz = pytz.timezone('America/Los_Angeles')

def utc2localdatetime(naive):
    """ input: naive utc timestamp from dataframe
        output: timestamp in local tz """

    #print("naive=", naive)

    utc = naive.tz_localize(timezone.utc)
    #print('utc=', utc)

    pac = utc.astimezone(pactz)
    #print('pac=', pac)

    return pac

def read_current_cases_df():
    gis = GIS() # This is publicly accessible so no login, right?
    table = Table(Config.COVID_DAILY_CASES_URL, gis)
    sdf = table.query(where="1=1", out_fields="*").sdf
    del table
#    ts = int(sdf.iloc[0]['date'] / 1000) # convert from mS
#    date = datetime.fromtimestamp(ts, timezone.utc).date()
#    df['date'] = date
    return sdf

def read_local_cases_df():
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    layer = FeatureLayer(Config.COVID_CASES_URL, gis)
    # Be careful, Esri 'where' clauses are very broken.
    # It would be elegant if they worked but, they don't.
    #sdf = layer.query(where="name=='Clatsop'", out_fields="*").sdf
    sdf = pd.DataFrame.spatial.from_layer(layer)
    df = sdf[(sdf['name']=='Clatsop') & (sdf['source']!='worldometer') & (sdf['source']!='OHA')]
    #print(df)
    return df

def crunch_data(sdf, days):
    """ Return two df's, one for total cases and one for daily cases. """

    # Convert to localtime
    # see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    date = []
    for utc_naive in sdf.loc[:, 'last_update']:
        # using date() here to toss out the time of day.
        date.append(utc2localdatetime(utc_naive).date())
    sdf['date'] = date

    if days > 0:
        start_date = datetime.utcnow() - timedelta(days)
        df = sdf[sdf['last_update'] >= start_date]

    df = df.set_index('date')
    df = df.sort_values("utc_date", ascending=True)
            
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


# ==================================================================================

# This is a unit test, it does no real work.

if __name__ == "__main__":

    # Read the accumulative table of many rows
    days = 10

    sdf = read_local_cases_df()
    last = sdf.sort_values("utc_date", ascending=False).iloc[0]

    (daily_df, total_df) = crunch_data(sdf, days)
    assert len(daily_df)>0
    assert len(total_df)>0

    print(daily_df.sort_values('date',ascending=False).iloc[0])
    print(total_df.sort_values('date',ascending=False).iloc[0])

    # Read the new, one row table.
    df = read_current_cases_df()
    assert len(df)==1
    current = df.iloc[0]

    print(last['new_cases'], current['new_cases'])
    print(last['total_cases'], current['total_cases'])
    dailytime = current['date']
    print(last['last_update'], dailytime)


# That's all!
