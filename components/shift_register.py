from collections import deque
from RPi import GPIO

from ..mixins import (
	ClearMixin,
	OutputEnableMixin,
)

## Set the pin mode:
GPIO.setmode (GPIO.BCM)

class ShiftRegister (
	ClearMixin,
	OutputEnableMixin,
):
	'''
		A class for handling a shift register
		using only three inputs.
	'''
	ON = 1
	OFF = 0

	def __init__ (self, **kwargs):
		'''
			A manager class for running
			a shift register on three
			given GPIO pins.
		'''
		super ().__init__ (*args, **kwargs)
		self.__number_outputs = kwargs.pop ('number_outputs')
		self.__data_pin_id = kwargs.pop ('data_pin_id')
		self.__clock_pin_id = kwargs.pop ('clock_pin_id')
		self.__latch_pin_id = kwargs.pop ('latch_pin_id')
		self.__number_unlatched = 0
		self.__written = deque (maxlen = len (self))
		self.__output = ()
		GPIO.setup (self.__data_pin_id, GPIO.OUT)
		GPIO.setup (self.__clock_pin_id, GPIO.OUT)
		GPIO.setup (self.__latch_pin_id, GPIO.OUT)
		## Ensure control is all initially off:
		self.__data_value = self.__clock_value = self.__latch_value = self.ON
		self.data_off ()
		self.clock_off ()
		self.latch_off ()
		## Ensure the output is clear:
		self.clear ()

	def __len__ (self):
		'''
			Return the number of outputs
			this instance is controlling.
		'''
		return self.__number_outputs

	@property
	def data_pin_on (self):
		'''
			Return a boolean for whether
			the data pin is currently on.
		'''
		return self.__data_value == self.ON

	@property
	def clock_pin_on (self):
		'''
			Return a boolean for whether
			the clock pin is currently on.
		'''
		return self.__clock_value == self.ON

	@property
	def latch_pin_on (self):
		'''
			Return a boolean for whether
			the latch pin is currently on.
		'''
		return self.__latch_value == self.ON

	@property
	def latched (self):
		'''
			Return a boolean for whether
			all data written has been latched.
		'''
		return not self.__number_unlatched

	@property
	def number_unlatched (self):
		'''
			Return the number of pieces of
			data written but not yet output.
		'''
		return self.__number_unlatched

	@property
	def output (self):
		'''
			Return the currently output data.
		'''
		return self.__output

	@property
	def written (self):
		'''
			Return the currently written data.
		'''
		return tuple (self.__written)

	def data_off (self):
		'''
			Turn the data pin off
			if it's not already.
		'''
		if self.data_pin_on:
			GPIO.output (self.__data_pin_id, GPIO.LOW)
			self.__data_value = self.OFF

	def clock_off (self):
		'''
			Turn the clock pin off
			if it's not already.
		'''
		if self.clock_pin_on:
			GPIO.output (self.__clock_pin_id, GPIO.LOW)
			self.__clock_value = self.OFF

	def latch_off (self):
		'''
			Turn the latch pin off
			if it's not already.
		'''
		if self.latch_pin_on:
			GPIO.output (self.__latch_pin_id, GPIO.LOW)
			self.__latch_value = self.OFF

	def data_on (self):
		'''
			Turn the data pin on
			if it's not already.
		'''
		if not self.data_pin_on:
			GPIO.output (self.__data_pin_id, GPIO.HIGH)
			self.__data_value = self.ON

	def clock_on (self):
		'''
			Turn the clock pin on
			if it's not already.
		'''
		if not self.clock_pin_on:
			GPIO.output (self.__clock_pin_id, GPIO.HIGH)
			self.__clock_value = self.ON
			## A rising clock line commits data
			## so all data is no longer latched:
			self.__number_unlatched += 1

	def latch_on (self):
		'''
			Turn the latch pin on
			if it's not already.
		'''
		if not self.latch_pin_on:
			GPIO.output (self.__latch_pin_id, GPIO.HIGH)
			self.__latch_value = self.ON
			## All data is latched again:
			self.__output = self.written
			self.__number_unlatched = 0

	def data (self):
		'''
			Pule the data pin.
		'''
		if self.data_pin_on:
			self.data_off ()
			self.data_on ()
		else:
			self.data_on ()
			self.data_off ()

	def clock (self):
		'''
			Pule the clock pin.
		'''
		if self.clock_pin_on:
			self.clock_off ()
			self.clock_on ()
		else:
			self.clock_on ()
			self.clock_off ()

	def latch (self):
		'''
			Pule the latch pin.
		'''
		if self.latch_pin_on:
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
		self.clock ()
		self.__written.appendleft (self.OFF)
		self.latch ()

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
		self.clock ()
		self.__written.appendleft (on_or_off)
		## Latch if requested:
		if latch:
			self.latch ()

	def all (self, on_or_off, latch = False):
		'''
			Write all data to the given on
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
		for i in range (len (self)):
			self.clock ()
			self.__written.appendleft (on_or_off)
		## Latch if requested:
		if latch:
			self.latch ()

	def clear (self):
		'''
			Turn off all outputs.
		'''
		## Use ClearMixin if possible for speed:
		if self.controlling_clear_pin:
			super ().clear ()
			self.latch ()
		else:
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
			Write values for outputs 1-x to from the given list.
			Data written in reverse so to_set[0] is
			set on pin 0 etc. Latch the result by default.
			Try reusing the previously written data by default.
		'''
		if reuse_previous:
			## Check if any of the currently
			## written data is of any use:
			already_written = list (self.__written)
			len_to_set = len (to_set)
			for i in range (len_to_set): ## to_set used in case shorter.
				if already_written[:len_to_set - i] == to_set[i:]:
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
			self.latch ()

	def from_pin_list (
		self,
		pin_list,
		latch = True,
		reuse_previous = True,
	):
		'''
			Write on to only the output numbers in
			the given list and off to all others.
			Pin numbering starts at 0.
			Latch the result by default.
			Try reusing the current data by default.
		'''
		to_write = [
			self.ON if pin in pin_list else self.OFF for pin in range (len (self))
		]
		self.from_list (
			to_write,
			latch = latch,
			reuse_previous = reuse_previous,
		)
