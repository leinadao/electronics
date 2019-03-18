from random import getrandbits as random_getrandbits
from time import (
	sleep as time_sleep,
	time as time_time,
)

from ..components import ShiftRegister

## Create a test shift register on pin 4 and 18:
test_shift_register = ShiftRegister (
	number_outputs = 16,
	data_pin_id = 4,
	clock_pin_id = 17,
	latch_pin_id = 18,
)

def flash_random (shift_register, iterations, pause_seconds):
	'''
		Iterate through the given number of random
		output configurations, pausing for the given
		number of seconds inbetween each, using
		the given shift register.
	'''
	for i in range (iterations):
		shift_register.from_list (
			[random_getrandbits (1) for a in range (shift_register.number_outputs)],
		)
		time_sleep (pause_seconds)

def test_average_time (shift_register, iterations):
	'''
		Test the speed of the furthest possible write,
		averaged over the given number of iterations.
	'''
	def test (shift_register):
		'''
			Time one write.
		'''
		a = time_time ()
		shift_register.from_list (
			[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
		)
		return time_time () - a
	test_results = [test () for i in range (iterations)]
	return sum (test_results) / len (test_results)
