"""Modes and database functions for projects db."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

######################################################

class Institution(db.Model):
	"""Institution model - institution name"""

	__tablename__ = 'institutions'

	institution_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	institution_name = db.Column(db.String(100), nullable=False)

	# relationships:
	users = db.relationship('Instit_Access')

	def __repr__(self):
		return(f'<institution_id={self.institution_id} institution_name={self.institution_name}>')


class Department(db.Model):
	"""departments model - departments located within an institution"""

	__tablename__ = 'departments'

	department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	department_name = db.Column(db.String(100), nullable=False)
	institution_id = db.Column(db.Integer, db.ForeignKey('institutions.institution_id'), nullable=False)

	# relationships:
	users = db.relationship('Dept_Access', backref='departments')

	def __repr__(self):
		return(f'<department_id={self.department_id} dept_name={self.department_name}')


class User(db.Model):
	"""User model - basic user information"""

	__tablename__ = 'users'

	user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	first_name = db.Column(db.String(30), nullable=False)
	last_name = db.Column(db.String(30), nullable=False)
	email = db.Column(db.Text, nullable=False)
	password = db.Column(db.Text, nullable=False)
	active = db.Column(db.Boolean, nullable=False)

	# relationships:
	projects = db.relationship('Project_Access')
	departments = db.relationship('Dept_Access')
	institution = db.relationship('Instit_Access')

	def __repr__(self):
		return(f'<user_id={self.user_id} email={self.email}>')


class Dept_Access(db.Model):
	"""Dept_Access model - contains access info for department"""

	__tablename__ = 'dept_access'

	access_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
	access_level = db.Column(db.String(10), nullable=False)

	# relationships:
	department = db.relationship('Department')

	def _repr__(self):
		return(f'<user_id={self.user_id} department_id={self.department_id} access={self.access_level}>')


class Instit_Access(db.Model):
	"""Instit_Access model - contains access info for institution"""

	__tablename__ = 'instit_access'

	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
	institution_id = db.Column(db.Integer, db.ForeignKey('institutions.institution_id'), primary_key=True)
	access_level = db.Column(db.String(10), nullable=False)

	def __repr__(self):
		return(f'<institution_id={self.institution_id} user_id={self.user_id} access={self.access_level}>')


class Access_Requests(db.Model):
	"""Access_Requests model - these are users requesting access to different departments"""

	__tablename__ = 'access_requests'

	request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)

	def __repr__(self):
		return(f'<request_id={self.request_id} user_id={self.user_id} department_id={self.department_id}>')


class Timezone(db.Model):
	"""Timezone Model - list of all timeszones to choose from"""

	__tablename__ = 'timezones'

	timezone_name = db.Column(db.String(50), primary_key=True)

	def __repr__(self):
		return(f'<timezone_name={self.timezone_name}>')


class Frequency(db.Model):
	"""Frequency Model - list of the frequencies to choose from"""

	__tablename__ = 'frequency'

	frequency = db.Column(db.String(20), primary_key=True)

	def __repr__(self):
		return(f'<frequency={self.frequency}>')


class Projects(db.Model):
	"""Project Model - all basic info for project"""

	__tablename__ = 'projects'

	project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	int_project_name = db.Column(db.String(100), nullable=False)
	ext_project_name = db.Column(db.String(100), nullable=False)
	project_creator = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
	timezone_name = db.Column(db.String(50), db.ForeignKey('timezones.timezone_name'), nullable=False)
	project_status = db.Column(db.String(20), nullable=False)

	# relationships:
	users = db.relationship('Project_Access')
	times = db.relationship('Project_Times')
	default_schedule = db.relationship('Project_Default_Schedule')
	blackouts = db.relationship('Blackouts')
	full_schedule = db.relationship('Participant_Schedule')


	def __repr__(self):
		return(f'<project_id={self.project_id} int_project_name={self.int_project_name}>')


class Project_Times(db.Model):
	"""Project_Times - list of default start and end times for each project"""

	__tablename__ = 'project_times'

	time_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	project_id = db. Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)
	start_time = db.Column(db.String(10), nullable=False)
	end_time = db.Column(db.String(10), nullable=False)

	def __repr__(self):
		return(f'<project_id={self.project_id} start={self.start_time} end={self.end_time}>')


class Project_Default_Schedule(db.Model):
	"""Project_Default_Schedule Model"""

	__tablename__ = 'project_default_schedule'

	proj_sched_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)
	frequency = db.Column(db.String(20), db.ForeignKey('frequency.frequency'), nullable=False)
	repeat_in = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return(f'<project_id={self.project_id} frequency={self.frequency} repeat_in={self.repeat_in}>')


class Blackouts(db.Model):
	"""Blackouts Model - details blackout dates per project"""

	__tablename__ = 'blackouts'

	blackout_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)
	blackout_name = db.Column(db.String(40), nullable=True)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)

	def __repr__(self):
		return(f'project_id={self.project_id} start={self.start} end={self.end}>')


class Project_Access(db.Model):
	"""Project Access model - keeps track of what level of access users have for each project"""

	__tablename__ = 'project_access'

	project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
	project_access = db.Column(db.String(20), nullable=False)

	def __repr__(self):
		return(f'<project_id={self.project_id} user_id={self.user_id} project_access={self.project_access}>')


class Participant_Schedule(db.Model):
	"""Participant_Schedule - has start and end times for each participant's appointment"""

	__tablename__ = 'participant_schedule'

	schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)
	participant_id = db.Column(db.Integer, nullable=False)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	scheduled_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

	def __repr__(self):
		return(f'<project_id={self.project_id} participant_id={self.participant_id} start={self.start} end={self.end}')


######################################################
# Helper functions

def init_app():
	# need to make a Flask app so we can use Flask-SQLAlchemy
	from flask import Flask
	app = Flask(__name__)

	connect_to_db(app)


def connect_to_db(app):
	"""Connect the database to our Flask app"""

	# Configure to use our database
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///projects'
	app.config['SQLALCHEMY_ECHO'] = False
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.app = app
	db.init_app(app)

if __name__ == '__main__':

	init_app()
	db.create_all()