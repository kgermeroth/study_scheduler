from model import *
from flask import session


def get_timezones():
	"""Returns a list of timezones from database"""

	timezones = []

	tz = Timezone.query.all()

	for zone in tz:
		timezones.append(zone.timezone_name)

	return timezones


def submit_project(submission):
	"""Takes project information and creates project in database"""

	int_project_name = submission['int_proj_name']
	ext_project_name = submission['ext_proj_name']
	department_id = submission['dept_choice']
	timezone_name = submission['timezone']

	project = Project(int_project_name=int_project_name,
					  ext_project_name=ext_project_name,
					  project_creator=session['user_id'],
					  department_id=department_id,
					  timezone_name=timezone_name,
					  project_status='active')

	db.session.add(project)
	db.session.commit()