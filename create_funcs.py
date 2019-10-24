from model import *
from flask import session


def get_timezones():
	"""Returns a list of timezones from database"""

	timezones = []

	tz = Timezone.query.all()

	for zone in tz:
		timezones.append(zone.timezone_name)

	return timezones


def check_project_dupes(submission):
	"""Checks database for duplicate project"""

	return Project.query.filter(Project.int_project_name == submission['int_proj_name']).all()


def submit_project(submission):
	"""Takes project information and creates project in database"""

	int_project_name = submission['int_proj_name']
	ext_project_name = submission['ext_proj_name']
	max_participants = int(submission['max_participants'])
	department_id = submission['dept_choice']
	timezone_name = submission['timezone']

	project = Project(int_project_name=int_project_name,
					  ext_project_name=ext_project_name,
					  max_participants=max_participants,
					  project_creator=session['user_id'],
					  department_id=department_id,
					  timezone_name=timezone_name,
					  project_status='active')

	db.session.add(project)
	db.session.commit()


def add_creator_to_proj_access(submission):
	"""Adds creator of project as admin to project_access table"""

	int_project_name = submission['int_proj_name']

	project = Project.query.filter(Project.int_project_name == int_project_name).first()

	access = Project_Access(project_id=project.project_id,
							user_id=session['user_id'],
							project_access='admin')

	db.session.add(access)
	db.session.commit()


