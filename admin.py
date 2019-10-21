from model import *

def print_options():
	"""Prints list of user options to the terminal"""

	print('Menu of items:')
	print('\tA: Add an institution')
	print('\tQ: Quit\n')


def choose_options():
	"""Takes user input and runs appropriate function"""
	
	keep_going = True

	available_options = {'A', 'Q'}	

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

if __name__ == '__main__':
	init_app()
	choose_options()