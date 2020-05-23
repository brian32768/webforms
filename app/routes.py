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

rest = "https://delta.co.clatsop.or.us/server/rest/services/TESTING_Brian/SDE_inventory_sandbox/FeatureServer"
portalUrl = "https://delta.co.clatsop.or.us/portal"
servicename = 'COVID19 Clatsop County Test Results'
layername = 'covid19_clatsop_test_results'

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

def connect(portal):
    global error
    # Amusingly the GIS search function is sloppy and returns several...
    # there does not appear to be an exact match option.
    search_result = []
    try:
        search_result = portal.content.search(servicename,
                                              item_type="Feature Service")
        if len(search_result) < 1:
            error = "Feature service '%s' not found." % layername
            return redirect("/fail")
    except Exception as e:
        print("Connection to feature service failed.", e)
        error = e
        return redirect('/fail')

    # Search for the correct Feature Service
    layer = None
    for item in search_result:
        #print(layername, item.title)
        if layername == item.title:
            layer = item.layers[0]
    if not layer:
        print("Connection to feature layer failed.")
        return redirect('/fail')

    return layer

@app.route('/', methods=['GET', 'POST'])
def update_cases():
    global error

    form = CasesForm()

    try:
        portal = GIS(portalUrl, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    except Exception as e:
        print("Connection to portal failed.", e)
        error = e
        return redirect('/fail')
    layer = connect(portal)
    
    if form.validate_on_submit():

        try:
            local = parsetime(form.datestamp.data)
            utc = local2utc(local).strftime(time_format)
        except Exception as e:
            print("Time format is confusing to me.",e)
            error = e
            return redirect("/fail")

        try:
            n = {"attributes": { 
                        "utc_date":    utc,
                        "positive":    int(form.positive.data),
                        "negative":    int(form.negative.data),
                        "total_tests": int(form.positive.data) + int(form.negative.data),
                        "recovered":   int(form.recovered.data),
                        "deaths":      int(form.deaths.data),
                        "editor":      "EMD",
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
        row = pd.DataFrame.spatial.from_layer(layer).sort_values(
            by=['utc_date'], ascending=False).head(1)
        s = row.iloc[0]

        old_date = s['utc_date']
        print(old_date.strftime(time_format))
        form.positive.data =  s['positive']
        form.negative.data =  s['negative']
        form.recovered.data = s['recovered']
        form.deaths.data =    s['deaths']
        #form.editor.data = s['editor']

    except Exception as e:
        print("Reading old data failed.", e)
        pass

    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    del portal

    return render_template('form.html', form=form)

# That's all!
