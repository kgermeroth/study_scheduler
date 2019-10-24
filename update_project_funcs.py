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