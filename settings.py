import sys
import re
import datetime

def processSettings(args):
	# First make sure that the user provided the minimum number of arguments (2):
	if len(args) < 2:
		print "Usage: recover.py [-dDRm] [flag arguments] <output folder> <start walk>"
		sys.exit(1)
	

	''' Each flag will trigger a specific function, specified in the 'all_settings' dict below.
	When adding a new setting, you must give it a 'func' and define a function for it here. '''

	def getMaxArguments(settings):
		max_arg = 0
		for key in settings:
			if 'arguments' in settings[key]:
				current_arg = settings[key]['arguments']
				if current_arg > max_arg:
					max_arg = current_arg
		return max_arg			

	def setMaxDays(key, str, settings):
		# Cast the argument to an int
		settings[key]['value'] = int(str)

	def switchRestore(key, settings):
		# Since restore is set to True by default, simply switch to False
		settings[key]['value'] = False

	def compileDate(value):
		# Convert the date string of format MM/DD/YYYY or MM/DD/YY to datetime
		# A helper function for all of the date options
		date_re = re.compile(r'(\d+)/(\d+)/(\d+)')

		search_month = int(date_re.search(value).groups()[0]) or None
		search_day = int(date_re.search(value).groups()[1]) or None
		search_year = int(date_re.search(value).groups()[2]) or None


		if search_month and search_day and search_year:
			return datetime.datetime(month=search_month, day=search_day, year=search_year)
		else:
			print "Date(s) must be in the format MM/DD/YY or MM/DD/YYYY"
			sys.exit(1)

	def getSingleDate(key, value, settings):
		# Sets the 'value' of 'search_date' to a single datetime object
		print "Looking for files deleted on %s" % value
		date = compileDate(value)
		settings[key]['value'] = date

	def getDateRange(key, values_array, settings):
		# Sets the 'value' of 'search_date_range' to a tuple of beginning and end datetimes
		print "Looking for files deleted between %s and %s" % (values_array[0], values_array[1])
		beginning = compileDate(values_array[0])
		end = compileDate(values_array[1])
		settings[key]['value'] = (beginning, end)		 


	# All of the possible settings (before processing)
	# If you want to add any available settings, this is where you'd do it.
	# If a given flag doesn't take any arguments, like -R, you must specify with 'arguments'.
	# Same goes if a given flag takes more than 1 argument
	all_settings = {
		# Sets the max days back a restoration should go (defaults to None)
		'max_days': { 'value': None, 'flag': '-m', 'arguments': 1, 'func': setMaxDays },

		# Switches whether or not to use Dropbox restore mode instead of copying files (default is True)
		'use_restore': { 'value': True, 'flag': '-R', 'arguments': 0, 'func': switchRestore },

		# Set a specific date on which files were deleted in order to restore them (default None)
		'search_date': { 'value': None, 'flag': '-d', 'arguments': 1, 'func': getSingleDate },

		# Set a range of dates in which files could have been deleted (default None)
		'search_date_range': { 'value': None, 'flag': '-D', 'arguments': 2, 'func': getDateRange },
	}

	''' Here is where the main processing of the arguments takes place.
	It will return a dictionary of settings and their values without any other information. '''
	max_args = getMaxArguments(all_settings)
	args_len = len(args)

	# Loop over system arguments
	''' This is kind of a mess for now. There is no error checking,
	so subsequent flags could be passed in as args '''
	for i in range(0, args_len - max_args):
		for key in all_settings:
			current_setting = all_settings[key]
			if current_setting['flag'] == args[i]:
				if current_setting['arguments'] > 1:
					values = []
					for x in range(0, current_setting['arguments']):
						values.append(args[i+x+1])
					current_setting['func'](key, values, all_settings)	
				elif current_setting['arguments'] == 1:
					current_setting['func'](key, args[i+1], all_settings)
				else:
					current_setting['func'](key, all_settings)

	# Return a dictionary with all settings values that have been set
	config = {}

	for key in all_settings:
		config[key] = all_settings[key]['value']
	config['start_walk'] = args[-1]
	config['recover_to'] = args[-2]	

	return config	
