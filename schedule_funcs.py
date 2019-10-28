"""This file contains all functions relating to scheduling participants"""

from model import *

def get_default_schedule(project_id):
	"""Returns a list of project schedule objects for a project (default schedule)"""

	return Project_Default_Schedule.query.filter(Project_Default_Schedule.project_id == project_id).all()


def get_timeslots(project_id):
	"""Returns a list of project time objects"""

	return Project_Times.query.filter(Project_Times.project_id == project_id).all()

