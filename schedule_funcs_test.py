import unittest, pytz
import schedule_funcs
from datetime import datetime, timedelta
from flask import session
from datetimerange import DateTimeRange
from model import *
from server import app

class ScheduleFuncsTest(unittest.TestCase):
	"""Unit tests for schedule_funcs module"""

	 # def setUp(self):
  #       """Stuff to do before every test."""

  #       # Get the Flask test client
  #       self.client = app.test_client()
  #       app.config['TESTING'] = True
  #       app.config['SECRET_KEY'] = os.environ['STUDY_SECRET_KEY']

  #       # Logs in test user
  #       with self.client as c:
  #           with c.session_transaction() as sess:
  #               sess['user_id'] = 1

  #       # Connect to test database
  #       connect_to_db(app, "postgresql:///testprojects")

  #       # Create tables and add sample data
  #       db.create_all()

	def test_has_conflicts_no_appts_exist(self):
		"""Tests scenario when no appts exist"""

		existing_appts = []

		max_participants = 1

		start_time = datetime(2019, 10, 31, 5, 0)
		end_time = datetime(2019, 10, 31, 6, 0)

		result = schedule_funcs.has_conflicts(existing_appts, start_time, end_time, max_participants)

		self.assertFalse(result)

	def test_has_conflicts_exceeds_max(self):
		"""Tests scenario when there are appointments and the overlap exceeds maximum"""

		existing_appts = [(datetime(2019, 10, 31, 5, 30), datetime(2019, 10, 31, 6, 30))]

		max_participants = 1

		start_time = datetime(2019, 10, 31, 5, 0)
		end_time = datetime(2019, 10, 31, 6, 0)

		result = schedule_funcs.has_conflicts(existing_appts, start_time, end_time, max_participants)

		self.assertTrue(result)

	def test_has_conflicts_max_not_exceeded(self):
		"""Tests when there are appointments but max is not exceeded"""

		existing_appts = [(datetime(2019, 10, 31, 5, 0), datetime(2019, 10, 31, 6, 0)),(datetime(2019, 10, 31, 6, 0), datetime(2019, 10, 31, 7, 0)) ]

		max_participants = 2

		start_time = datetime(2019, 10, 31, 5, 30)
		end_time = datetime(2019, 10, 31, 6, 30)

		result = schedule_funcs.has_conflicts(existing_appts, start_time, end_time, max_participants)

		self.assertFalse(result)


if __name__ == '__main__':
	
	unittest.main()



