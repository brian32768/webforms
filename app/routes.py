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

county_centroid = {"x": -123.74, "y": 46.09}

time_format = "%m/%d/%Y %H:%M"

error = "ERROR 99999" # yes it's a global variable, sorry

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
    #print(search_result)
    if len(search_result) < 1:
        error = "Feature service '%s' not found." % layername
        raise Exception(error)

    # Search for the correct Feature Service
    try:
        layercollection = [
            item for item in search_result if item.title == layertitle][0]
    except IndexError:
        print(layercollection)
        raise Exception('Layer not found. "%s"' % layertitle)

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
                "geometry": county_centroid
            }
        except Exception as e:
            print("Attribute error.", e)
            error = e
            return redirect("/fail")

        results = ''
        try:
            print(layer, n)
            results = layer.edit_features(adds=[n])
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
        #print(s)

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

def percent(n,d):
    if n and d:
        fn = s2f(n)
        fd = s2f(d)
        if fd != 0:
            return round(fn * 100.0 / fd, 0)
    return 0

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
    # We have INPUT and now we're going to SAVE it.

        #session['name'] = form.name.data

        try:
            # The form has local time and we need UTC
            local = parsetime(form.datestamp.data)
            utc = local2utc(local).strftime(time_format)
        except Exception as e:
            print("Time format is confusing to me.", e)
            error = e
            return redirect("/fail")

        try:
            n = {"attributes": {
                "utc_date":        utc,
                "editor":          VERSION,
                'facility':        'Clatsop',

                "n95_date":        utc,
                "n95":             s2i(form.n95.data),
                "n95_burn":        s2i(form.n95_burn.data),
                "n95_goal":        s2i(form.n95_goal.data),
                "n95_complete":    percent(form.n95.data, form.n95_goal.data),

                "mask_date":       utc,
                "mask":            s2i(form.mask.data),
                "mask_burn":       s2i(form.mask_burn.data),
                "mask_goal":       s2i(form.mask_goal.data),
                "mask_complete":   percent(form.mask.data, form.mask_goal.data),

                "shield_date":     utc,
                "shield":          s2f(form.shield.data),
                "shield_burn":     s2f(form.shield_burn.data),
                "shield_goal":     s2f(form.shield_goal.data),
                "shield_complete": percent(form.shield.data, form.shield_goal.data),

                "glove_date":      utc,
                "glove":           s2i(form.glove.data),
                "glove_burn":      s2i(form.glove_burn.data),
                "glove_goal":      s2i(form.glove_goal.data),
                "glove_complete":  percent(form.glove.data, form.glove_goal.data),

                "gown_date":       utc,
                "gown":            s2i(form.gown.data),
                "gown_burn":       s2i(form.gown_burn.data),
                "gown_goal":       s2i(form.gown_goal.data),
                "gown_complete":   percent(form.gown.data, form.gown_goal.data),

                "coverall_date":   utc,
                "coverall":        s2i(form.coverall.data),
                "coverall_burn":   s2i(form.coverall_burn.data),
                "coverall_goal":   s2i(form.coverall_goal.data),
                "coverall_complete": percent(form.coverall.data, form.coverall_goal.data),

                "sanitizer_date":  utc,
                "sanitizer":       s2f(form.sanitizer.data),
                "sanitizer_burn":  s2f(form.sanitizer_burn.data),
                "sanitizer_goal":  s2f(form.sanitizer_goal.data),
                "sanitizer_complete":  percent(form.sanitizer.data, form.sanitizer_goal.data),

                "goggle_date":     utc,
                "goggle":          s2i(form.goggle.data),
                "goggle_burn":     s2i(form.goggle_burn.data),
                "goggle_goal":     s2i(form.goggle_goal.data),
                "goggle_complete": percent(form.goggle.data, form.goggle_goal.data),

            },
                "geometry": county_centroid
            }
        except Exception as e:
            print("Attribute error.", e)
            error = e
            return redirect("/fail")

        results = ''
        try:
            #print(layer, n)
            results = layer.edit_features(adds=[n])
        except Exception as e:
            error = str(e) + ' -- make sure the layer is owned by sde not DBO'
            print("Write failed", e)
            return redirect("/fail")

        return redirect('/thanks')

    # We need input so we're sending the form.

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
        form.n95_goal.data = s['n95_goal']
        form.n95_complete.data = s['n95_complete']

        form.mask.data = s['mask']
        form.mask_burn.data = s['mask_burn']
        form.mask_goal.data = s['mask_goal']
        form.mask_complete.data = s['mask_complete']

        form.shield.data = s['shield']
        form.shield_burn.data = s['shield_burn']
        form.shield_goal.data = s['shield_goal']
        form.shield_complete.data = s['shield_complete']

        form.glove.data = s['glove']
        form.glove_burn.data = s['glove_burn']
        form.glove_goal.data = s['glove_goal']
        form.glove_complete.data = s['glove_complete']

        form.gown.data = s['gown']
        form.gown_burn.data = s['gown_burn']
        form.gown_goal.data = s['gown_goal']
        form.gown_complete.data = s['gown_complete']

        form.sanitizer.data = s['sanitizer']
        form.sanitizer_burn.data = s['sanitizer_burn']
        form.sanitizer_goal.data = s['sanitizer_goal']
        form.sanitizer_complete.data = s['sanitizer_complete']

        form.goggle.data = s['goggle']
        form.goggle_burn.data = s['goggle_burn']
        form.goggle_goal.data = s['goggle_goal']
        form.goggle_complete.data = s['goggle_complete']

        form.coverall.data = s['coverall']
        form.coverall_burn.data = s['coverall_burn']
        form.coverall_goal.data = s['coverall_goal']
        form.coverall_complete.data = s['coverall_complete']

    except Exception as e:
        print("Reading old data failed.", e)
        pass

    # Show the current local time in the form.
    now = datetime.now()
    ds = now.strftime(time_format)
    form.datestamp.data = ds

    html = 'ppe_hoscap.html'
    if facility == 'Clatsop':
        html = 'ppe.html'

    return render_template(html, form=form)


# That's all!
