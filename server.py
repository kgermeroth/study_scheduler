"""Master file for running server. Includes managing all routes"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import *

import os
import register_funcs, util, create_funcs, update_project_funcs

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
			session['instit_id'] = user.institution[0].institution_id
			flash('You have been successfully logged in!')
			return redirect('/')

		else:
			flash('Provided password was incorrect.')
			return redirect('/login')


@app.route('/')
def display_home():
	"""Displays project home page"""

	proj_list = util.get_users_projects()

	return render_template('home.html', proj_list=proj_list)


@app.route('/create')
def display_create_page():
	"""Displays project creation page"""

	avail_depts = util.get_user_departments()

	timezones = create_funcs.get_timezones()

	return render_template('create.html', avail_depts=avail_depts, timezones=timezones)


@app.route('/create-project', methods=["POST"])
def create_project():
	"""Adds project to database"""

	submission = request.form

	# check to see if project exists
	if create_funcs.check_project_dupes(submission) is None:
		flash('A project with this name already exists')
		return redirect('/create')

	create_funcs.submit_project(submission)

	create_funcs.add_creator_to_proj_access(submission)

	flash('Your project has been created!')

	return redirect('/')


@app.route('/project/<project_id>')
def display_project_dashboard(project_id):
	"""Displays a project_dashboard for each project"""

	access = util.check_project_access(project_id)
	# check to see if a user even has rights, if not, return user to home
	if access is None:
		flash('You do not have access to that project.')
		return redirect('/')

	return render_template('dashboard.html', access=access)


@app.route('/manage/<project_id>')
def display_manage_project_page(project_id):
	"""Displays the manage project page"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if (access is None) or (access.project_access != 'admin'):
		flash('You do not have access to this page.')
		return redirect('/')

	return render_template('manage.html', access=access)


@app.route('/details/<project_id>')
def display_details_page(project_id):
	"""Displays the project details page"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if (access is None) or (access.project_access != 'admin'):
		flash('You do not have access to this page.')
		return redirect('/')

	return render_template('details.html', access=access)


@app.route('/update-project-details', methods=['POST'])
def update_project_details():
	"""Takes form submission and updates project details"""

	submission = request.form

	update_project_funcs.submit_project_updates(submission)

	flash('Your project details have been updated!')

	redirect_addy = '/details/' + str(submission['project_id'])

	return redirect(redirect_addy)


@app.route('/timeslots/<project_id>')
def display_timeslots_page(project_id):
	"""Displays timeslots management page"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if (access is None) or (access.project_access != 'admin'):
		flash('You do not have access to this page.')
		return redirect('/')

	times = update_project_funcs.package_time_info()

	return render_template('timeslots.html', access=access, times=times)

if __name__ == '__main__':

    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')