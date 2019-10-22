from model import *

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

