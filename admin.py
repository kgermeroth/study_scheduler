from model import *

def print_options():
	"""Prints list of user options to the terminal"""

	print('Menu of items:')
	print('\tA: Add an institution')
	print('\tB: Add a department to an institution')
	print('\tQ: Quit\n')


def choose_options():
	"""Takes user input and runs appropriate function"""
	
	keep_going = True

	available_options = {'A', 'B', 'Q'}	

	while keep_going:

		print_options()

		admin_choice = input('Enter the letter option for desired task: ').upper()

		# check to see if the user input is valid
		if admin_choice not in available_options:
			print('I\'m sorry, that is not a valid choice. Please choose from the above options.\n')

		# if user chooses 'Q' for quit
		elif admin_choice == 'Q':
			print('You are now leaving the program. Have a wonderful day!')
			break

		# if user chooses 'A' for 'Add an Institution'
		elif admin_choice == 'A':
			add_institution()

		# if user chooses 'B' for add a department
		elif admin_choice == 'B':
			add_departments()


def add_institution():
	"""Adds an institution to the database"""

	print('\nYou will be adding a new institution to the database.\n')
	institution_to_add = input('What is the name of the institution to add?: ')
	print()

	# double check the spelling
	confirm = input(f'Is "{institution_to_add}" correct? Confirm Y or N: ').upper()

	# if not correct start over
	if confirm.startswith('N'):
		print()
		return

	# if correct, add institution to the database
	else:
		institution = Institution(institution_name=institution_to_add)
		db.session.add(institution)
		db.session.commit()
		print(f'\n"{institution_to_add}" has been successfully added.\n')


def add_departments():
	"""Adds department to a given institution"""

	instit_dict = {}

	# get a list of institutions from database
	institutions = Institution.query.all()

	print('You have chosen to add a department to an institution.\n')

	print('Available institutions:')
	# print out a list of institutions and create a dictionary
	for institution in institutions:
		inst_id, inst_name = institution.institution_id, institution.institution_name
		instit_dict[inst_id] = inst_name
		print(f'{inst_id}: {inst_name}')

	# have user select from list of options
	chosen_instit = input('\nChoose the number of institution to add department to: ')

	# check user input to verify valid
	if not ((chosen_instit.isdigit()) and (int(chosen_instit) in instit_dict)):
		print('That is not a valid selection.\n')
		return

	chosen_instit = int(chosen_instit)

	# if valid, have user enter name of department
	dept_to_add = input('\nPlease enter department name: ')

	# confirm to user entry is correct
	print(f'\nYou would like to add "{dept_to_add}" to "{instit_dict[chosen_instit]}"?')
	confirm = input('Y or N? ').upper()

	# if no, return
	if confirm.startswith('N'):
		print()
		return

	# if yes, add to database and confirm to user it has been updated
	location = Location(department_name=dept_to_add, institution_id=chosen_instit)
	db.session.add(location)
	db.session.commit()

	print(f'\n"{dept_to_add}" has been added to the database.\n')


if __name__ == '__main__':
	init_app()
	choose_options()