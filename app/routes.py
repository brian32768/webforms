from IPython.display import display
from flask import render_template, redirect, flash
from app import app
from app.forms import CasesForm
from config import Config

import os
from arcgis.gis import GIS

from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

rest = "https://delta.co.clatsop.or.us/server/rest/services/TESTING_Brian/SDE_inventory_sandbox/FeatureServer"
portal = "https://delta.co.clatsop.or.us/portal"
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

@app.route('/', methods=['GET', 'POST'])
def update_cases():
    global error

    form = CasesForm()

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

        # Amusingly the GIS search function is sloppy and returns several...
        # there does not appear to be an exact match option.
        search_result = []
        try:
            delta = GIS(portal, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
            search_result = delta.content.search(servicename,
                item_type="Feature Service")
            if len(search_result) < 1:
                error = "Feature service '%s' not found." % layername
                return redirect("/fail")
        except Exception as e:
            print("Connection to feature service failed.", e)
            error = e
            return redirect("/fail")

        # Search for the correct Feature Service
        layer = None
        for item in search_result:
            #print(layername, item.title)
            if layername == item.title:
                layer = item.layers[0]
        if not layer:
            print("Connection to feature layer failed.")
            return redirect("/fail")

        results = ''
        try:
            results = layer.edit_features(adds=[n])
            print(results['addResults'][0]['success'])
        except Exception as e:
            error = e
            print("Write failed", e, results)
            return redirect("/fail")

        del delta  # release connection
        return redirect('/thanks')

    else :
        print("form errors: ", form.errors)
        flash(form.errors)

    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    return render_template('form.html', form=form)

# That's all!
