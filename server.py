"""Master file for running server. Includes managing all routes"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import *

import os
import register_funcs, util, create_funcs, update_project_funcs, schedule_funcs

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

	project = create_funcs.add_creator_to_proj_access(submission)

	flash('Your project has been created!')

	redirect_addy = '/manage/' + str(project.project_id)

	return redirect(redirect_addy)


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

	existing_times = update_project_funcs.get_existing_timeslots(project_id)

	return render_template('timeslots.html', access=access, times=times, existing_times=existing_times)


@app.route('/submit-timeslot', methods=['POST'])
def submit_timeslot():
	"""Take user input and add timeslot to the database"""

	submission = request.form

	update_project_funcs.submit_new_timeslot(submission)

	flash('Your timeslot has been added.')

	redirect_addy = '/timeslots/' + str(submission['project_id'])

	return redirect(redirect_addy)	


@app.route('/delete-timeslot', methods=['POST'])
def delete_timeslot():
	""""Deletes appropriate timeslots"""

	submission = request.form

	update_project_funcs.delete_timeslots(submission)

	flash('Your timeslots have been deleted.')

	redirect_addy = '/timeslots/' + str(submission['project_id'])

	return redirect(redirect_addy)	


@app.route('/users/<project_id>')
def display_users_page(project_id):
	"""Display users page"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if (access is None) or (access.project_access != 'admin'):
		flash('You do not have access to this page.')
		return redirect('/')

	avail_dept_users, proj_users = update_project_funcs.get_user_info(project_id)

	levels = ['view', 'edit', 'admin']

	return render_template('users.html', 
						   access=access, 
						   dept_users=avail_dept_users, 
						   proj_users=proj_users,
						   levels=levels)	


@app.route('/add-user', methods=["POST"])
def add_user_to_project():
	"""Adds a user to a project with correct permissions"""

	submission = request.form

	update_project_funcs.add_user_to_project(submission)

	flash('User has been added to the project.')

	redirect_addy = '/users/' + str(submission['project_id'])

	return redirect(redirect_addy)	


@app.route('/change-users', methods=["POST"])
def process_user_changes():
	"""Makes changes to project_access"""

	submission = request.form

	update_project_funcs.process_user_changes(submission)

	flash('User changes have been updated')

	redirect_addy = '/users/' + str(submission['project_id'])

	return redirect(redirect_addy)	


@app.route('/schedule/<project_id>')
def display_schedule_homepage(project_id):
	"""Displays project homepage"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if access is None:
		flash('You do not have access to this page.')
		return redirect('/')

	return render_template('schedule_home.html', access=access)


@app.route('/schedule-appt')
def reroute_to_schedule_pg():
	"""Routes user to appropriate scheduling page"""

	submission = request.args

	print(submission)

	redirect_addy = '/schedule/' + str(submission['project_id']) + '/' + submission['participant_id']

	return redirect(redirect_addy)


@app.route('/schedule/<project_id>/<participant_id>')
def display_part_scheduling_page(project_id, participant_id):
	"""Displays scheduling page"""

	access = util.check_project_access(project_id)

	# check to see if a user even has rights, if not, return user to home
	if access is None:
		flash('You do not have access to this page.')
		return redirect('/')

	frequencies = util.get_frequencies(project_id)

	timeslots = schedule_funcs.get_timeslots(project_id)

	project_defaults = schedule_funcs.get_default_schedule(project_id)

	appointments = schedule_funcs.get_participant_appointments(project_id, participant_id)

	appointments = schedule_funcs.format_appointments(appointments, project_id)

	return render_template('schedule_page.html', 
						   access=access, 
						   participant_id=participant_id,
						   frequencies=frequencies, 
						   timeslots=timeslots,
						   project_defaults=project_defaults,
						   appointments=appointments)


@app.route('/confirm/<project_id>/<participant_id>')
def check_date_conflicts(project_id, participant_id):
	"""Takes user input, calculates dates, and checks for conflicts"""

	submission = request.args

	try:
		no_conflict_dates, conflict_dates = schedule_funcs.check_conflicts_master(submission)

	except:
		raise ValueError('Not all of the fields were filled out, please try again.')

	return render_template('confirm_schedule.html', 
							project_id=project_id,
							participant_id=participant_id,
							no_conflict_dates=no_conflict_dates,
							conflict_dates=conflict_dates)


@app.route('/confirm-schedules', methods=['POST'])
def book_appointments():
	"""Takes information and adds appointments to the database"""

	submission = request.form

	dates = schedule_funcs.convert_confirmed_dates(submission)

	schedule_funcs.schedule_dates(submission['project_id'], submission['participant_id'], dates)

	redirect_addy = '/schedule/' + str(submission['project_id']) + '/' + str(submission['participant_id'])

	return redirect(redirect_addy)

@app.route('/delete-appointment', methods=['POST'])
def delete_appointments():
	"""Handles deletion of appointments"""

	submission = request.form

	schedule_funcs.delete_appointment(submission)

	flash('Your appointments have been cancelled')

	redirect_addy = '/schedule/' +str(submission['project_id']) + '/' + str(submission['participant_id'])

	return redirect(redirect_addy)


if __name__ == '__main__':

    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')