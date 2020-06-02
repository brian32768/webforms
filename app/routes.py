from IPython.display import display
from flask import render_template, redirect, flash
from app import app
from app.forms import CasesForm, PPEForm
from config import Config

import os
from arcgis.gis import GIS
import pandas as pd

from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

VERSION = 'webforms 1.1'

portal_url      = Config.PORTAL_URL
portal_user     = Config.PORTAL_USER
portal_password = Config.PORTAL_PASSWORD

cases_layer = Config.CASES_LAYER
cases_title = Config.CASES_TITLE
ppe_layer   = Config.PPE_LAYER
ppe_title   = Config.PPE_TITLE

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

def connect(portal, layername, layertitle):
    # Amusingly the GIS search function is sloppy and returns several...
    # there does not appear to be an exact match option.
    search_result = portal.content.search(query=layername,
                                          item_type="Feature Layer Collection")
    print(search_result)
    if len(search_result) < 1:
        error = "Feature service '%s' not found." % layername
        raise Exception(error)

    # Search for the correct Feature Service
    layercollection = [
        item for item in search_result if item.title == layertitle][0]
    print(layercollection)

    return layercollection.layers[0]


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')

@app.route('/cases', methods=['GET', 'POST'])
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
        layer = connect(portal, cases_layer, cases_title)
    except Exception as e:
        print("Connection to Cases feature service failed.", e)
        error = e
        return redirect('/fail')

    if form.validate_on_submit():

        #session['name'] = form.name.data

        try:
            local = parsetime(form.datestamp.data)
            utc = local2utc(local).strftime(time_format)
        except Exception as e:
            print("Time format is confusing to me.", e)
            error = e
            return redirect("/fail")

        try:
            n = {"attributes": {
                "utc_date":        utc,
                "last_update":     utc,
                'name':            'Clatsop',
                "total_cases":     s2i(form.positive.data),
                "total_negative":  s2i(form.negative.data),
                "total_tests":     s2i(form.positive.data)
                + s2i(form.negative.data),
                "total_recovered": s2i(form.recovered.data),
                "total_deaths":    s2i(form.deaths.data),

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
        newest = clatsop_df.sort_values(
            by=['utc_date'], ascending=False).head(1)
        #print(newest)
        s = newest.iloc[0]
        print(s)

        # Force the old date into UTC
        old_date = s['utc_date'].replace(tzinfo=timezone('UTC'))
        # Show the old date in the local TZ
        form.old_date = "(previous %s)" % old_date.astimezone(
            timezone('America/Los_Angeles')).strftime(time_format)

        form.positive.data = s['total_cases']
        form.negative.data = s['total_negative']
        form.recovered.data = s['total_recovered']
        form.deaths.data = s['total_deaths']
        #form.editor.data =    s['editor']

    except Exception as e:
        print("Reading old data failed.", e)
        pass

    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    del portal

    return render_template('cases.html', form=form)

def s2i(s):
    """ Convert a string to an integer even if it has + and , in it. """
    if s == None or s == '':
        return None
    if type(s) == type(0):
        # This is already an integer
        return s
    if s:
        return int(float(s.replace(',', '')))
    return None

def s2f(s):
    """ Convert a string to a float even if it has + and , in it. """
    if s == None or s == '':
        return None
    if type(s) == type(0.0) or type(s) == type(0):
        # Already a number
        return s
    if s:
        return float(s.replace(',', ''))
    return None

@app.route('/ppe/<facility>', methods=['GET', 'POST'])
def update_ppe(facility="Clatsop"):
    global error

    if not facility in ['Clatsop', 'PSH', 'CMH']:
        error = 'Could not recognize the facilty name'
        return redirect('/fail')

    form = PPEForm()

    try:
        portal = GIS(portal_url, portal_user, portal_password)
    except Exception as e:
        print("Connection to portal failed.", e)
        error = e
        return redirect('/fail')
    try:
        layer = connect(portal, ppe_layer, ppe_title)
    except Exception as e:
        print("Connection to PPE feature service failed.", e)
        error = e
        return redirect('/fail')

    if form.validate_on_submit():

        #session['name'] = form.name.data

        try:
            local = parsetime(form.datestamp.data)
            utc = local2utc(local).strftime(time_format)
        except Exception as e:
            print("Time format is confusing to me.", e)
            error = e
            return redirect("/fail")

        try:
            n = {"attributes": {
                "utc_date":        utc,
                "editor":          "EMD",
                'facility':        'Clatsop',

                "n95_date":        utc,
                "n95":             s2i(form.n95.data),
                "n95_burn":        s2i(form.n95_burn.data),

                "mask_date":       utc,
                "mask":            s2i(form.mask.data),
                "mask_burn":       s2i(form.mask_burn.data),

                "shield_date":     utc,
                "shield":          s2i(form.shield.data),
                "shield_burn":     s2i(form.shield_burn.data),

                "glove_date":      utc,
                "glove":           s2i(form.glove.data),
                "glove_burn":      s2i(form.glove_burn.data),

                "gown_date":       utc,
                "gown":            s2i(form.gown.data),
                "gown_burn":       s2i(form.gown_burn.data),

                "coverall_date":   utc,
                "coverall":        s2i(form.coverall.data),
                "coverall_burn":   s2i(form.coverall_burn.data),

                "sanitizer_date":  utc,
                "sanitizer":       s2f(form.sanitizer.data),
                "sanitizer_burn":  s2f(form.sanitizer_burn.data),

                "goggle_date":     utc,
                "goggle":          s2i(form.goggle.data),
                "goggle_burn":     s2i(form.goggle_burn.data),

            },
                "geometry": {
                "x": -123.74, "y": 46.09  # county centroid, more or less
            }}
        except Exception as e:
            print("Attribute error.", e)
            error = e
            return redirect("/fail")

        results = ''
        try:
            results = layer.edit_features(adds=[n])
            #print(results['addResults'][0]['success'])
        except Exception as e:
            error = e
            print("Write failed", e, results)
            return redirect("/fail")

        return redirect('/thanks')

    try:
        # Try to populate the form with the newest values
        df = pd.DataFrame.spatial.from_layer(layer)
        #print(df)

        clatsop_df = df[df.facility == facility]
        #print(clatsop_df)
        newest = clatsop_df.sort_values(
            by=['utc_date'], ascending=False).head(1)
        #print(newest)
        s = newest.iloc[0]
        print(s)

        # Force the old date into UTC
        old_date = s['utc_date'].replace(tzinfo=timezone('UTC'))
        # Show the old date in the local TZ
        form.old_date = "(previous %s)" % old_date.astimezone(
            timezone('America/Los_Angeles')).strftime(time_format)

        form.facility.data = s['facility']

        form.n95.data = s['n95']
        form.n95_burn.data = s['n95_burn']
        form.mask.data = s['mask']
        form.mask_burn.data = s['mask_burn']
        form.shield.data = s['shield']
        form.shield_burn.data = s['shield_burn']
        form.glove.data = s['glove']
        form.glove_burn.data = s['glove_burn']
        form.gown.data = s['gown']
        form.gown_burn.data = s['gown_burn']

        form.sanitizer.data = s['sanitizer']
        form.sanitizer_burn.data = s['sanitizer_burn']
        form.goggle.data = s['goggle']
        form.goggle_burn.data = s['goggle_burn']
        form.coverall.data = s['coverall']
        form.coverall_burn.data = s['coverall_burn']

    except Exception as e:
        print("Reading old data failed.", e)
        pass

    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    del portal

    html = 'ppe_hoscap.html'
    if facility == 'Clatsop':
        html = 'ppe.html'

    return render_template(html, form=form)


# That's all!
