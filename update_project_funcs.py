"""These are all functions that pertain to all actions that can be taken from the manage screen.

Includes: updating project details, setting and deleting timeslots, and managing users"""

from model import *

def submit_project_updates(submission):
	"""Takes submitted info and updates the project"""

	# get the project object
	project = Project.query.filter(Project.project_id == int(submission['project_id'])).first()

	# update attributes:
	project.int_project_name = submission['int_proj_name']
	project.ext_project_name = submission['ext_proj_name']
	project.max_participants = submission['max_participants']

	db.session.add(project)
	db.session.commit()

######### Functions for timeslots page ##############

def package_time_info():
	"""Returns a list of time information. 

	format = [[hours], [minutes], [AM, PM]]"""

	hours = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
	minutes = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']
	tod = ['AM', 'PM']

	return [hours, minutes, tod]


def get_existing_timeslots(project_id):
	"""Gets a list of existing timeslots"""

	return Project_Times.query.filter(Project_Times.project_id == project_id).all() 


def submit_new_timeslot(submission):
	"""Takes user submission and add new timeslot to the database"""

	start = submission['start_hour'] + ":" + submission['start_minute'] + " " + submission['start_AM_PM']
	end = submission['end_hour'] + ":" + submission['end_minute'] + " " + submission['end_AM_PM']

	new_time = Project_Times(project_id=submission['project_id'], start_time=start, end_time=end)

	db.session.add(new_time)
	db.session.commit()


def delete_timeslots(submission):
	"""Deletes selected timeslots from database"""

	to_delete = [int(timeslot) for timeslot in submission.getlist('delete_timeslot')]

	for timeslot in to_delete:
		timeslot = Project_Times.query.filter(Project_Times.time_id == timeslot).first()

		db.session.delete(timeslot)
		db.session.commit()

######### Functions for users page ##############

def get_users_in_dept(dept_id):
	"""Returns a list of all users in a given department"""

	return Dept_Access.query.filter(Dept_Access.department_id == dept_id).all()


def get_users_for_project(proj_id):
	"""Returns a list of Proj_Access objects who have access to project"""

	return Project_Access.query.filter(Project_Access.project_id == proj_id).all()


def get_user_info(proj_id):
	"""Returns a tuple of users who can be added, and users who are already in place

	(avail_dept_users ((list of dept_access objects), proj_users ((list of project_access objects)) )"""

	proj_users = get_users_for_project(proj_id)

	dept_users = get_users_in_dept(proj_users[0].project.department_id)

	proj_users_set = set()

	for user in proj_users:
		proj_users_set.add(user.user_id)

	avail_dept_users = []

	for user in dept_users:
		if user.user_id not in proj_users_set:
			avail_dept_users.append(user)

	return (avail_dept_users, proj_users)


def add_user_to_project(submission):
	"""Takes provided information and adds user to the project"""

	project_id = int(submission['project_id'])
	user_id = int(submission['new_user'])
	access = submission['access_level']

	new_user = Project_Access(project_id=project_id, user_id=user_id, project_access=access)

	db.session.add(new_user)
	db.session.commit()


def process_user_changes(submission):
	"""Takes changes to user and process them"""

	user_changes = parse_data(submission)

	for user in user_changes:
		proj_user = Project_Access.query.filter(Project_Access.user_id == user, Project_Access.project_id == submission['project_id']).one()

		# check to see if user should be deleted first and if yes, delete the user
		if user_changes[user]['remove']:
			db.session.delete(proj_user)

		# otherwise process the changes
		else:
			proj_user.project_access = user_changes[user]['access']
			db.session.add(proj_user)

		db.session.commit()


def parse_data(submission):
	"""Takes the submission and parses out to match submissions with user_id
	returns dict with following format: 
		{'user_id' : {'access':access, 'remove':False}}"""

	users = submission.getlist('user_id')

	user_actions = {}

	for user in users:
		actions = {}

		# each key is the name followed by user_id, need to look up those specific keys

		# start with access level
		key = 'access_level' + user

		access = submission[key]

		actions['access'] = access

		# next with removal, but if a user is not being removed it will not appear

		try:
			key = 'remove_access' + user

			removal = submission[key]

			actions['remove'] = True
		except:
			actions['remove'] = False

		user_actions[int(user)] = actions

	return user_actions



