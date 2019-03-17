from collections import deque
from RPi import GPIO

## Set the pin mode:
GPIO.setmode (GPIO.BCM)

class ShiftRegister ():
	'''
		A class for handling a shift register
		using only three inputs.
	'''
	ON = 1
	OFF = 0

	def __init__ (
		self,
		number_outputs,
		data_pin_id,
		clock_pin_id,
		latch_pin_id,
		clear = False,
	):
		'''
			A manager class for running
			a shift register on three
			given GPIO pins.
		'''
		self.__number_outputs = number_outputs
		self.__data_pin_id = data_pin_id
		self.__clock_pin_id = clock_pin_id
		self.__latch_pin_id = latch_pin_id
		self.__latched = False
		self.__output = deque (maxlen = self.__number_outputs)
		GPIO.setup (self.__data_pin_id, GPIO.OUT)
		GPIO.setup (self.__clock_pin_id, GPIO.OUT)
		GPIO.setup (self.__latch_pin_id, GPIO.OUT)
		## Ensure it's all initially turned off:
		self.all_pins_off () ## Also initialises statuses as off.
		## Make sure the output is
		## clear if requested:
		if clear:
			self.clear ()

	@property
	def number_outputs (self):
		'''
			Return the number of outputs
			this instance is controlling.
		'''
		return self.__number_outputs

	@property
	def data (self):
		'''
			Return a boolean for whether
			the data pin is currently on.
		'''
		return self.__data == self.ON

	@property
	def clock (self):
		'''
			Return a boolean for whether
			the clock pin is currently on.
		'''
		return self.__clock == self.ON

	@property
	def latch (self):
		'''
			Return a boolean for whether
			the latch pin is currently on.
		'''
		return self.__latch == self.ON

	@property
	def latched (self):
		'''
			Return a boolean for whether
			all data written has been latched.
		'''
		return self.__latched

	def data_off (self):
		'''
			Turn the data pin off
			if it's not already.
		'''
		if self.data:
			GPIO.output (self.__data_pin_id, GPIO.LOW)
			self.__data = self.OFF

	def clock_off (self):
		'''
			Turn the clock pin off
			if it's not already.
		'''
		if self.clock:
			GPIO.output (self.__clock_pin_id, GPIO.LOW)
			self.__clock = self.OFF

	def latch_off (self):
		'''
			Turn the latch pin off
			if it's not already.
		'''
		if self.latch:
			GPIO.output (self.__latch_pin_id, GPIO.LOW)
			self.__latch = self.OFF

	def all_pins_off (self):
		'''
			Turn all pins off.
		'''
		self.data_off ()
		self.clock_off ()
		self.latch_off ()

	def data_on (self):
		'''
			Turn the data pin on
			if it's not already.
		'''
		if not self.data:
			GPIO.output (self.__data_pin_id, GPIO.HIGH)
			self.__data = self.ON

	def clock_on (self):
		'''
			Turn the clock pin on
			if it's not already.
		'''
		if not self.clock:
			GPIO.output (self.__clock_pin_id, GPIO.HIGH)
			self.__clock = self.ON
			## A rising clock line commits data
			## so all data is no longer latched:
			self.__latched = False

	def latch_on (self):
		'''
			Turn the latch pin on
			if it's not already.
		'''
		if not self.latch:
			GPIO.output (self.__latch_pin_id, GPIO.HIGH)
			self.__latch = self.ON
			## All data is latched again:
			self.__latched = True

	def all_pins_on (self):
		'''
			Turn all pins on.
		'''
		self.data_on ()
		self.clock_on ()
		self.latch_on ()

	def data_pulse (self):
		'''
			Pule the data pin.
		'''
		if self.data:
			self.data_off ()
			self.data_on ()
		else:
			self.data_on ()
			self.data_off ()

	def clock_pulse (self):
		'''
			Pule the clock pin.
		'''
		if self.clock:
			self.clock_off ()
			self.clock_on ()
		else:
			self.clock_on ()
			self.clock_off ()

	def latch_pulse (self):
		'''
			Pule the latch pin.
		'''
		if self.latch:
			self.latch_off ()
			self.latch_on ()
		else:
			self.latch_on ()
			self.latch_off ()

	def shift (self):
		'''
			Shift the current data along,
			ensuring no data is added.
		'''
		## Make sure data isn't added:
		self.data_off ()
		self.clock_pulse ()
		self.__output.append (self.OFF)
		self.latch_pulse ()

	def next (self, on_or_off, latch = False):
		'''
			Set the next value to the given
			on or off value and latch if requested.
		'''
		## Ensure data is ready:
		if on_or_off:
			self.data_on ()
		else:
			self.data_off ()
		## Ensure clock ready:
		self.clock_off ()
		## Commit the data:
		self.clock_pulse ()
		self.__output.append (on_or_off)
		## Latch if requested:
		if latch:
			self.latch_pulse ()

	def all (self, on_or_off, latch = False):
		'''
			Set all outputs to the given on
			or off value and latch if requested.
			Doesn't use next for efficiency.
		'''
		## Ensure data is ready:
		if on_or_off:
			self.data_on ()
		else:
			self.data_off ()
		## Ensure clock ready:
		self.clock_off ()
		## Commit the data:
		for i in range (self.__number_outputs):
			self.clock_pulse ()
			self.__output.append (on_or_off)
		## Latch if requested:
		if latch:
			self.latch_pulse ()

	def clear (self):
		'''
			Turn off all outputs.
		'''
		self.all (
			self.OFF,
			latch = True,
		)

	def from_list (
		self,
		to_set,
		latch = True,
		reuse_previous = True,
	):
		'''
			Set outputs 1-x to from the given list.
			Data written in reverse so to_set[0] is
			set on pin 0 etc. Latch the result by default.
			Try reusing the previous output by default.
		'''
		if reuse_previous:
			## Check if any of the current
			## output is of any use:
			output = list (self.__output)
			len_to_set = len (to_set)
			for i in range (len_to_set): ## to_set used in case shorter.
				if output[:len_to_set - i] == to_set[i:]:
					to_set = to_set[:i]
		## Reverse the list so order is
		## maintained once written:
		to_set.reverse ()
		## Iterate through the list:
		for v in to_set:
			self.next (v)
		## Only latch at the end for
		## efficiency, if requested:
		if latch:
			self.latch_pulse ()

	def from_pin_list (
		self,
		pin_list,
		latch = True,
		reuse_previous = True,
	):
		'''
			Turn on only the output numbers in
			the given list and all others off.
			Pin numbering starts at 0.
			Latch the result by default.
			Try reusing the previous output by default.
		'''
		data = [
			self.ON if pin in pin_list else self.OFF for pin in range (self.__number_outputs)
		]
		self.from_list (
			data,
			latch = latch,
			reuse_previous = reuse_previous,
		)
