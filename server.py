"""Master file for running server. Includes managing all routes"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import *

import os

app = Flask(__name__)

# required to run Flask sessions and debug toolbar
app.secret_key = os.environ['STUDY_SECRET_KEY']

# gives an error in jinga template if undefined variable rather than failing silently
app.jinja_env.undefined = StrictUndefined

@app.route('/register')
def display_register_page():
	"""Displays the user registration form"""

	instit_list = []
	# get institution data and add to institution dict
	institutions = Institution.query.all()

	for institution in institutions:
		instit_list.append((institution.institution_id, institution.institution_name))

	# get departments for first institution
	dept_list = []

	departments = Location.query.filter(Location.institution_id == instit_list[0][0]).all()

	for dept in departments:
		dept_list.append((dept.location_id, dept.department_name))

	return render_template('register.html', instit_list=instit_list, dept_list=dept_list)

if __name__ == '__main__':

    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')