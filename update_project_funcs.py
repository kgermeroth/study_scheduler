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
