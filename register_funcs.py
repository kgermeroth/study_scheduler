from model import *
import util

def get_instits():
	"""Gets a list of all institution_ids and names in tuple format"""

	instit_list = []
	# get institution data and add to institution dict
	institutions = Institution.query.all()

	for institution in institutions:
		instit_list.append((institution.institution_id, institution.institution_name))

	
	return instit_list


def get_depts(institution_id):
	"""Gets a list of all department_ids and names in tuple format for an institution"""

	dept_list = []

	departments = Location.query.filter(Location.institution_id == institution_id).all()

	for dept in departments:
		dept_list.append((dept.location_id, dept.department_name))

	return dept_list


def add_new_user(submission):
	"""Adds user to database in users table"""

	first_name = submission['first_name']
	last_name = submission['last_name']
	email = submission['email_address']
	password = submission['password']
	institution_id = submission['institution_choice']

	password = util.hash_password(password)

	new_user = User(first_name=first_name,
					last_name=last_name,
					email=email,
					password=password,
					institution_id=institution_id,
					active=True)

	db.session.add(new_user)
	db.session.commit()


def add_location_for_user(user_id, submission):
	"""Adds a location for a specific user"""

	location_id = submission['location_choice']

	access = User_Access(user_id=user_id, location_id=location_id, access_level='user')

	db.session.add(access)
	db.session.commit()


def complete_registration(submission):
	"""Does full user_registration process"""

	email = submission['email_address']

	# add to users table:
	add_new_user(submission)

	# get the new user_id:
	user_id = util.get_user_by_email(email).user_id

	# add location for user
	add_location_for_user(user_id, submission)







