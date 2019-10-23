from model import *


def get_timezones():
	"""Returns a list of timezones from database"""

	timezones = []

	tz = Timezone.query.all()

	for zone in tz:
		timezones.append(zone.timezone_name)

	return timezones