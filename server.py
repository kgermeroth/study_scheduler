"""Master file for running server. Includes managing all routes"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import *

import os
import register_funcs

app = Flask(__name__)

# required to run Flask sessions and debug toolbar
app.secret_key = os.environ['STUDY_SECRET_KEY']

# gives an error in jinga template if undefined variable rather than failing silently
app.jinja_env.undefined = StrictUndefined

@app.route('/register')
def display_register_page():
	"""Displays the user registration form"""

	instit_list = register_funcs.get_instits()

	dept_list = register_funcs.get_depts(instit_list[0][0])

	return render_template('register.html', instit_list=instit_list, dept_list=dept_list)


@app.route('/get-new-departments.json')
def get_new_departments():
	"""Gets new departments and returns data in json"""

	submission = request.args

	dept_list = register_funcs.get_depts(submission['institChoice'])

	return jsonify(dept_list)


@app.route('/register', methods=['POST'])
def register_user():
	"""Takes form inputs and adds user to database"""

	submission = request.form
	email = submission['email_address']

	if register_funcs.get_user_by_email(email):
		flash('This email address already exists')

	else:
		# add to users table:
		register_funcs.add_new_user(submission)

		# get the new user_id:
		user_id = register_funcs.get_user_by_email(email).user_id

		# add location for user
		register_funcs.add_location_for_user(user_id, submission)

		flash(f'"{email}" has been successfully added as a user')

	return redirect('/register')



if __name__ == '__main__':

    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')