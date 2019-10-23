"""Master file for running server. Includes managing all routes"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import *

import os
import register_funcs, util, create_funcs

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

	if util.get_user_by_email(email):
		flash('This email address already exists')

	else:
		register_funcs.complete_registration(submission)

		flash(f'"{email}" has been successfully added as a user')

	return redirect('/login')


@app.route('/login')
def display_login_page():
	"""Displays login page"""

	return render_template('login.html')


@app.route('/login-verification')
def verify_login_information():
	"""Checks user input against database"""

	submission = request.args

	email = submission['email']
	pwd = submission['password']

	user = util.get_user_by_email(email)

	if user is None:
		flash('This email does not exist. Please check spelling or register')
		return redirect('/login')

	else:
		# check to see if the password matches
		pwd_match = util.verify_password(user.password, pwd)

		if pwd_match:
			session['user_id'] = user.user_id
			flash('You have been successfully logged in!')
			return redirect('/')

		else:
			flash('Provided password was incorrect.')
			return redirect('/login')


@app.route('/')
def display_home():
	"""Displays project home page"""

	return render_template('home.html')


@app.route('/create')
def display_create_page():
	"""Displays project creation page"""

	avail_departments = util.get_user_departments()

	timezones = create_funcs.get_timezones()

	return render_template('create.html', avail_departments=avail_departments, timezones=timezones)






if __name__ == '__main__':

    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')