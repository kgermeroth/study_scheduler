"""Modes and database functions for projects db."""

from flask_sqlalchemy import flask_sqlalchemy

db = SQLAlchemy()

######################################################

class Institution(db.Model):
	"""Institution model - institution name"""

	__tablename__ = 'institution'

	institution_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	institution_name = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return(f'<institution_id={self.institution_id} institution_name={self.institution_name}>')


class Location(db.Model):
	"""Location model - departments located within an institution"""

	__tablename__ = 'location'

	location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	department_name = db.Column(db.String(100), nullable=False)
	institution_id = db.Column(db.Integer, db.ForeignKey('institution.institution_id'), nullable=False)

	def __repr__(self):
		return(f'<location_id={self.location_id} dept_name={self.department_name}')


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

	def __repr__(self):
		return(f'<user_id={self.user_id} email={self.email}>')


class User_Access(db.Model):
	"""User_Access model - contains access info for institution and department"""

	__tablename__ = 'user_access'

	access_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)
	access_level = db.Column(db.String(10), nullable=False)

	def _repr__(self):
		return(f'<user_id={self.user_id} location_id={self.location_id} access={self.access_level}>')


class Access_Requests(db.Model):
	"""Access_Requests model - these are users requesting access to different departments"""

	__tablename__ = 'access_requests'

	request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=False)

	def __repr__(self):
		print(f'<request_id={self.request_id} user_id={self.user_id} location_id={self.location_id}>')




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