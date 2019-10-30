"""This file contains all functions relating to scheduling participants"""

from model import *
from datetime import datetime, timedelta
from flask import session
import pytz

def get_default_schedule(project_id):
	"""Returns a list of project schedule objects for a project (default schedule)"""

	return Project_Default_Schedule.query.filter(Project_Default_Schedule.project_id == project_id).all()


def get_timeslots(project_id):
	"""Returns a list of project time objects"""

	return Project_Times.query.filter(Project_Times.project_id == project_id).all()


def parse_timeframes_from_submission(submission):
	"""Takes submission and parses into usable format.

	Returns [{'freq' : 'once', 'repeat_in' : 5, 'start_date' : datetime, 'end_date' : datetime}, {etc}]"""

	parsed_timeframes = []

	ids = submission.getlist('div_ids')

	for d in ids:
		timeframe_dict = {}

		# pull out frequency and add to dictionary
		freq = 'freq_' + d
		freq = submission[freq]
		timeframe_dict['freq'] = freq

		# pull out repetition and add to dictionary
		rep = 'repeat_in_' + d
		rep = submission[rep]
		timeframe_dict['repeat_in'] = rep

		# take dates and convert them into datetime objects
		start_day = 'starting_on_' + d
		start_day = submission[start_day]

		time = 'time_' + d
		time = submission[time]

		start_time, end_time = convert_to_military_time(time)

		# convert start to a datetime object
		start_datetime = start_day + 'T' + start_time

		start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')

		timeframe_dict['start_date'] = start_datetime

		# calculate end date (in case it goes around the clock)
		timeframe_dict['end_date'] = calculate_end_datetime(start_datetime, start_time, end_time)

		parsed_timeframes.append(timeframe_dict)

	return parsed_timeframes


def convert_to_military_time(time):
	"""Returns start and end time as military time

	>>>'11:00 AM - 01:00 PM' 
	('11:00', '13:00') 			"""

	start_hour = int(time[:2])
	start_minutes = time[3:5]
	start_meridian = time[6:8]

	start_time = convert_hours_military(start_hour, start_meridian) + ":" + start_minutes

	end_hour = int(time[-8:-6])
	end_minutes = time[-5:-3]
	end_meridian = time[-2:]

	end_time = convert_hours_military(end_hour, end_meridian) + ":" + end_minutes

	return(start_time, end_time)


def convert_hours_military(hour, meridian):
	"""Takes hour and am/pm and returns the hour in military as a string"""

	if hour == 12:
		hour = 0

	if meridian == 'PM':
		hour += 12

	padded_hour = '{:02}'.format(hour)

	return str(padded_hour)


def calculate_end_datetime(start_datetime, start_time, end_time):
	"""Takes start as datetime and end time as string and returns end as datetime object"""

	start_hour = int(start_time[:2])
	end_hour = int(end_time[:2])
	end_minutes = int(end_time[-2:])

	# if the end hour is greater than or equal to the start time it is the same day
	# replace the hour and minutes in the start datetime object
	if end_hour >= start_hour:
		return start_datetime.replace(hour=end_hour, minute=end_minutes)

	# if it's not, that means it goes into early the next day, so add one to the datetime object
	# and then replace the hour and minutes
	else:
		end_date = start_datetime + timedelta(days=1)
		return end_date.replace(hour=end_hour, minute=end_minutes)


def calculate_needed_dates(timeframes):
	"""Takes in a list of parsed timeframes and returns a list of tuples of calculated datetime objects
	[(start_datetime, end_datetime)]   """

	calculated_dates = []

	for timeframe in timeframes:

		# if the event is only happening once, add the repeat_in value to the start and end dates
		if timeframe['freq'] == 'once':
			days = int(timeframe['repeat_in'])
			start_date = timeframe['start_date'] + timedelta(days=days)
			end_date = timeframe['end_date'] + timedelta(days=days)

			calculated_dates.append((start_date, end_date))

		# if it is daily, add starting dates to list and then add one day until correct number is reached
		elif timeframe['freq'] == 'daily':
			start_date = timeframe['start_date']
			end_date = timeframe['end_date']

			calculated_dates.append((start_date, end_date))

			i = 1

			while i < int(timeframe['repeat_in']):
				start_date = start_date + timedelta(days=1)
				end_date = end_date + timedelta(days=1)

				calculated_dates.append((start_date, end_date))

				i += 1

		# else it is weekly, add starting dates to list and then add seven days until correct number is reached
		else:
			start_date = timeframe['start_date']
			end_date = timeframe['end_date']

			calculated_dates.append((start_date, end_date))

			i = 1

			while i < int(timeframe['repeat_in']):
				start_date = start_date + timedelta(days=7)
				end_date = end_date + timedelta(days=7)

				calculated_dates.append((start_date, end_date))

				i += 1

	return calculated_dates


def check_for_conflicts(calculated_dates, project_id):
	"""Takes calculated dates and checks for conflicts

	returns a tuple (no_conflict_dates, conflict_dates)"""

	pass


def check_conflicts_master(submission):
	"""Handles all parts of checking date conflicts"""

	parsed_timeframes = parse_timeframes_from_submission(submission)

	calculated_dates = calculate_needed_dates(parsed_timeframes)

	#@TODO check for conflicts

	return calculated_dates


def schedule_dates(project_id, participant_id, dates):
	"""Takes a list of dates and adds them to the database"""

	project = Project.query.filter(Project.project_id == project_id).one()

	proj_tz = pytz.timezone(project.timezone_name)

	utc = pytz.timezone('UTC')

	for date in dates:
		# localize dates
		start_date = proj_tz.localize(date[0])
		end_date = proj_tz.localize(date[1])

		# convert dates to UTC
		start_utc = start_date.astimezone(utc)
		end_utc = end_date.astimezone(utc)

		schedule = Participant_Schedule(
										project_id=project_id,
										participant_id=participant_id,
										start=start_utc,
										end=end_utc,
										scheduled_by=session['user_id'])

		db.session.add(schedule)
		db.session.commit()

