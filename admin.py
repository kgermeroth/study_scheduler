def print_options():
	"""Prints list of user options to the terminal"""

	print('Menu of items:')
	print('\tA: Add an institution')
	print('\tQ: Quit')


def choose_options():
	"""Takes user input and runs appropriate function"""
	
	keep_going = True

	available_options = {'A', 'Q'}	

	while keep_going is True:

		print_options()

		admin_choice = input('Enter the letter option for desired task: ').upper()

		# check to see if the user input is valid
		if admin_choice not in available_options:
			print('I\'m sorry, that is not a valid choice. Please choose from the above options.\n')

		# if user chooses 'Q' for quit
		elif admin_choice == 'Q':
			print('You are now leaving the program. Have a wonderful day!')
			break


def add_institution():
	"""Adds an institution to the database"""

	pass

if __name__ == '__main__':

	choose_options()