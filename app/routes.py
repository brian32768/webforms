from IPython.display import display
from flask import render_template, redirect, flash
from app import app
from app.forms import CasesForm
from config import Config

import os
from arcgis.gis import GIS
import pandas as pd

from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

VERSION = 'webforms 1.0'

portal_url      = Config.PORTAL_URL
feature_layer   = Config.PORTAL_FEATURE_LAYER
portal_user     = Config.PORTAL_USER
portal_password = Config.PORTAL_PASSWORD

time_format = "%m/%d/%Y %H:%M"

error = "ERROR 99999" # yes it's a global

def parsetime(s) :
    """ Parse a time string and return a datetime object. """
    return datetime.strptime(s, time_format)

def local2utc(t):
    """ Change a datetime object from local to UTC """
    return t.astimezone(timezone('UTC'))

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/fail')
def fail(e=""):
    return render_template("fail.html", error=error)

def connect(portal, feature_layer):
    # Amusingly the GIS search function is sloppy and returns several...
    # there does not appear to be an exact match option.
    search_result = portal.content.search(query=feature_layer,
                                          item_type="Feature Layer Collection")
    if len(search_result) < 1:
        error = "Feature service '%s' not found." % feature_layer
        raise Exception(error)

    # Search for the correct Feature Service
    layercollection = [
        item for item in search_result if item.title == feature_layer][0]

    return layercollection.layers[0]

@app.route('/', methods=['GET', 'POST'])
def update_cases():
    global error

    form = CasesForm()

    try:
        portal = GIS(portal_url, portal_user, portal_password)
    except Exception as e:
        print("Connection to portal failed.", e)
        error = e
        return redirect('/fail')
    try:
        layer = connect(portal, feature_layer)
    except Exception as e:
        print("Connection to feature service failed.", e)
        error = e
        return redirect('/fail')

    if form.validate_on_submit():

        #session['name'] = form.name.data

        try:
            local = parsetime(form.datestamp.data)
            utc = local2utc(local).strftime(time_format)
        except Exception as e:
            print("Time format is confusing to me.",e)
            error = e
            return redirect("/fail")

        try:
            n = {"attributes": { 
                        "utc_date":        utc,
                        "last_update":     utc,
                        'name':            'Clatsop',
                        "total_cases":     int(float(form.positive.data)),
                        "total_negative":  int(float(form.negative.data)),
                        "total_tests":     int(float(form.positive.data)) 
                                         + int(float(form.negative.data)),
                        "total_recovered": int(float(form.recovered.data)),
                        "total_deaths":    int(float(form.deaths.data)),

                        "source":          VERSION,
                        "editor":          "EMD",
                    },
                "geometry": {
                    "x": -123.74, "y": 46.09  # county centroid, more or less
                    }
                }
        except Exception as e:
            print("Attribute error.", e)
            error = e
            return redirect("/fail")

        results = ''
        try:
            results = layer.edit_features(adds=[n])
            print(results['addResults'][0]['success'])
        except Exception as e:
            error = e
            print("Write failed", e, results)
            return redirect("/fail")

        return redirect('/thanks')

    try:
        # Try to populate the form with the newest values
        df = pd.DataFrame.spatial.from_layer(layer)
        #print(df)
        clatsop_df = df[df.name == 'Clatsop']
        #print(clatsop_df)
        newest = clatsop_df.sort_values(by=['utc_date'], ascending=False).head(1)
        #print(newest)
        s = newest.iloc[0]
        print(s)

        # Force the old date into UTC
        old_date = s['utc_date'].replace(tzinfo=timezone('UTC'))
        # Show the old date in the local TZ
        form.old_date = "(previous %s)" % old_date.astimezone(timezone('America/Los_Angeles')).strftime(time_format)

        form.positive.data =  s['total_cases']
        form.negative.data =  s['total_negative']
        form.recovered.data = s['total_recovered']
        form.deaths.data =    s['total_deaths']
        #form.editor.data =    s['editor']

    except Exception as e:
        print("Reading old data failed.", e)
        pass

    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    del portal

    return render_template('form.html', form=form)

# That's all!
