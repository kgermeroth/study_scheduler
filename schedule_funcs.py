"""This file contains all functions relating to scheduling participants"""

from model import *
from datetime import datetime, timedelta
from flask import session
from datetimerange import DateTimeRange
import pytz

UTC = pytz.timezone('UTC')

def get_default_schedule(project_id):
	"""Returns a list of project schedule objects for a project (default schedule)"""

	return Project_Default_Schedule.query.filter(Project_Default_Schedule.project_id == project_id).all()


def get_timeslots(project_id):
	"""Returns a list of project time objects"""

	return Project_Times.query.filter(Project_Times.project_id == project_id).all()


def get_participant_appointments(project_id, participant_id):
	"""Returns a list of participant schedule objects to display already scheduled appointments"""

	appointments = Participant_Schedule.query.filter(Participant_Schedule.project_id == project_id, 
													 Participant_Schedule.participant_id == participant_id).all()

	appointments.sort(key=lambda a: a.start)

	return appointments


def format_appointments(appointments, project_id):
	"""Takes in list of participant schedule objects, converts to project timezone, formats dates, returns five part tuple:
		(schedule_id, start, end, book_by_first, book_by_last"""

	pretty_appts = []	

	project = Project.query.filter(Project.project_id == project_id).one()

	tz = pytz.timezone(project.timezone_name)

	for appt in appointments:
		start = convert_prettify_appointments(appt.start, tz)

		# if appointment starts and ends the same day, no need to include date in the end
		if appt.start.date() == appt.end.date():
			end = convert_prettify_sameday_appt(appt.end, tz)
		else:
			end = convert_prettify_appointments(appt.end, tz)

		pretty_appts.append((appt.schedule_id, start, end, appt.user_info.first_name, appt.user_info.last_name))

	return pretty_appts


def convert_prettify_appointments(appt_time, proj_timezone):
	"""Takes in participant schedule object, converts to proper timezone, formats into nice string"""

	# specify timezone is UTC
	appt_time = appt_time.astimezone(UTC)

	# change timezone to project timezone
	appt_time = appt_time.astimezone(proj_timezone)

	# format it into a nice string
	return appt_time.strftime('%Y-%m-%d (%a) %I:%M %p')


def convert_prettify_sameday_appt(appt_time, proj_timezone):
	"""Takes in participant schedule object, converts to proper timezone, formats into nice string with time only"""

	# specify timezone is UTC
	appt_time = appt_time.astimezone(UTC)

	# change timezone to project timezone
	appt_time = appt_time.astimezone(proj_timezone)

	# format it into a nice string
	return appt_time.strftime('%I:%M %p')


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
	"""Takes calculated dates (list of tuple(start,end) and checks for conflicts

	returns a tuple (no_conflict_dates, conflict_dates)"""

	no_conflict_dates = []
	conflict_dates = []

	project = Project.query.filter(Project.project_id == project_id).one()

	max_participants = project.max_participants

	tz = pytz.timezone(project.timezone_name)

	for date in calculated_dates:
		start = date[0]
		end = date[1]

		# convert to timezone and localize 
		start = tz.localize(start)
		end = tz.localize(end)
		
		# convert to utc for comparison purposes
		start_utc = start.astimezone(UTC)
		end_utc = end.astimezone(UTC)

		#@TODO - check blackouts first. If yes, add to conflict list

		overlaps = get_overlapping_appointments(start_utc, end_utc, project_id)
		if overlaps:
			((o.start, o.end) for o in overlaps)

		# add dates from no_conflict_dates list to overlaps to make sure there are no conflicts with those
		overlaps.extend(no_conflict_dates)

		if not overlaps:
			no_conflict_dates.append((start, end))

		else:
			if has_conflicts(overlaps, start_utc, end_utc, max_participants):
				conflict_dates.append((start, end))

			else:
				no_conflict_dates.append((start, end))

	return (no_conflict_dates, conflict_dates)


def get_overlapping_appointments(start_utc, end_utc, project_id):
	"""Returns a list of overlapping Participant_Schedule database objects"""

	# do a query for overlaps that start before start date
	overlap_pre = Participant_Schedule.query.filter(Participant_Schedule.project_id == project_id, 
													Participant_Schedule.start <= start_utc,
													Participant_Schedule.end > start_utc).all()
	# do a query for overlaps that start after start date
	overlap_post = Participant_Schedule.query.filter(Participant_Schedule.project_id == project_id,
													Participant_Schedule.start > start_utc,
													Participant_Schedule.start < end_utc).all()
	# combine overlaps (these are in UTC)
	overlaps = overlap_pre + overlap_post

	return overlaps


def has_conflicts(existing_appts, start_time, end_time, max_participants):
	"""Returns True if the date has a conflict, False if the date does not"""

	# create dict where key is tuples in 5 minute increments with start and end
	mini_frames = {}

	mf_end_time = start_time + timedelta(minutes=5) 

	mini_frames[(start_time, mf_end_time)] = 0

	while mf_end_time <= end_time:
		# the new start is equal to the old end, and the new end is 5 minutes later
		mf_start_time = mf_end_time
		mf_end_time = mf_start_time + timedelta(minutes=5)

		mini_frames[(mf_start_time, mf_end_time)] = 0

	# go through each date in the overlap list and compare to each key in the timeframe
	for appt in existing_appts:
		for mini_frame in mini_frames:

			# use date time range to see if there is an intersection
			appt_range = DateTimeRange(appt[0].astimezone(UTC), appt[1].astimezone(UTC))
			mini_range = DateTimeRange(mini_frame[0].astimezone(UTC), mini_frame[1].astimezone(UTC))

			# need to check to see if the intersection is valid - calculates the intersection
			# makes sure it is valid (there is one) and that it isn't zero (this would happen if the end of an appt, ie 9AM, is the start of a mini_frame range)
			intersection = appt_range.intersection(mini_range)
			if intersection.is_valid_timerange() and intersection.get_timedelta_second() != 0:
				mini_frames[mini_frame] += 1
				
			# check to see if the new value is equal to max participants. If it is return True
			if mini_frames[mini_frame] >= max_participants:
				return True

	return False


def check_conflicts_master(submission):
	"""Handles all parts of checking date conflicts"""

	parsed_timeframes = parse_timeframes_from_submission(submission)

	calculated_dates = calculate_needed_dates(parsed_timeframes)

	no_conflict_dates, conflict_dates = check_for_conflicts(calculated_dates, submission['project_id'])

	no_conflict_dates.sort(key=lambda d: d[0])
	no_conflict_dates = simple_prettify(no_conflict_dates)

	conflict_dates.sort(key=lambda d: d[0])
	conflict_dates = simple_prettify(conflict_dates)

	return (no_conflict_dates, conflict_dates)


def simple_prettify(dates):
	"""Takes naive date tuple of (start, end) and converts into nice format"""

	pretty_dates = []

	for date in dates:
		start = date[0]
		end = date[1]

		start = start.strftime('%Y-%m-%d (%a)  %I:%M %p')

		if date[0].date() == end.date():
			end = end.strftime('%I:%M %p')
		else:
			end = end.strftime('%Y-%m-%d (%a) %I:%M %p')

		pretty_dates.append((start, end))

	return pretty_dates


def convert_confirmed_dates(submission):
	"""Takes dates confirmed dates from user and converts them into proper datetime objects.
	Comes in format of '2019-11-05 (Tue) 08:00 AM - 09:00 AM' or '2019-11-05 (Tue) 11:00 PM - 2019-11-06 (Wed) 01:00 AM'
	Returns a list of tuples of (start, end)"""

	pretty_dates = []

	date_strings = submission.getlist('no_conflict')

	for date_string in date_strings:
		# separate into start and end
		start, end = date_string.split(' - ')

		start_date = start[:10]

		if len(end) > 8:
			end_date = end[:10]
		else:
			end_date = start_date

		time_range = start[-8:] + ' - ' + end[-8:]

		start_time, end_time = convert_to_military_time(time_range)

		start_datetime = start_date + 'T' + start_time
		end_datetime = end_date + 'T' + end_time

		start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
		end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')

		pretty_dates.append((start_datetime, end_datetime))

	return pretty_dates


def schedule_dates(project_id, participant_id, dates):
	"""Takes a list of dates and adds them to the database"""

	project = Project.query.filter(Project.project_id == project_id).one()

	proj_tz = pytz.timezone(project.timezone_name)

	for date in dates:
		# localize dates
		start_date = proj_tz.localize(date[0])
		end_date = proj_tz.localize(date[1])

		# convert dates to UTC
		start_utc = start_date.astimezone(UTC)
		end_utc = end_date.astimezone(UTC)

		schedule = Participant_Schedule(
										project_id=project_id,
										participant_id=participant_id,
										start=start_utc,
										end=end_utc,
										scheduled_by=session['user_id'])

		db.session.add(schedule)
		db.session.commit()


def delete_appointment(submission):
	"""Deletes appointments"""

	# get the list of schedule ids that were in the form
	sched_ids = submission.getlist('schedule_id')

	# go through schedule ids and recreate the name of the submissions that might exist
	for sched_id in sched_ids:
		key = 'delete_appoint_' + sched_id

		try:
			delete = submission[key]

			sched_to_delete = Participant_Schedule.query.filter(Participant_Schedule.schedule_id == int(sched_id)).one()

			db.session.delete(sched_to_delete)

			db.session.commit()

		except:
			continue


