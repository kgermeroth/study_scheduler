"""Utility file to seed hotels database from collected data"""

from sqlalchemy import func
from model import connect_to_db, db, init_app, Timezone, Frequency

def load_frequencies():
	"""Loads frequncies from text file into database."""

	# open file where data is stored
	file = open('seed_files/frequency.txt')

	# loop through each line and add it to the database
	for line in file:
		line = line.rstrip()

		# instantiate a Frequncy object and add it to database
		frequency = Frequency(frequency=line)

		db.session.add(frequency)

	db.session.commit()

	file.close()


def load_timezones():
	"""Loads timezones from text file into database."""

	# open file where data is stored
	file = open('seed_files/timezones.txt')

	# loop through each line and add it to the database
	for line in file:
		line = line.rstrip()

		# instantiate a Timezone object and add it to the database
		timezone = Timezone(timezone_name=line)

		db.session.add(timezone)

	db.session.commit()

	file.close()


if __name__ == "__main__":
	init_app()

	# delete all rows in table in case need to import multiple times
	
	Frequency.query.delete()
	Timezone.query.delete()

	load_frequencies()
	load_timezones()