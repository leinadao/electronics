import RPi.GPIO as GPIO

## Set the pin mode:
GPIO.setmode (GPIO.BCM)

class ShiftRegister ():
	'''
		A class for handling a test shift register.
	'''
	ON = 1
	OFF = 0

	def __init__ (
		self,
		number_outputs,
		data_pin_id,
		clock_pin_id,
		latch_pin_id,
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
		GPIO.setup (self.__data_pin_id, GPIO.OUT)
		GPIO.setup (self.__clock_pin_id, GPIO.OUT)
		GPIO.setup (self.__latch_pin_id, GPIO.OUT)
		## Ensure it's all initially turned off:
		self.all_pins_off () ## Also initialises statuses as off.

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

	def latch_on (self):
		'''
			Turn the latch pin on
			if it's not already.
		'''
		if not self.latch:
			GPIO.output (self.__latch_pin_id, GPIO.HIGH)
			self.__latch = self.ON

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
		## Latch if requested:
		if latch:
			self.latch_pulse ()

	def set_all (self, on_or_off):
		'''
			Set all values to the given
			on or off value.
		'''
		for i in range (self.__number_outputs):
			self.next (on_or_off)

	def set_all_and_latch (self, on_or_off):
		'''
			Set all values to the given
			on or off value and latch it.
		'''
		for i in range (self.__number_outputs):
			self.next (
				on_or_off,
				latch = True,
			)

	def clear (self):
		'''
			Turn off all outputs.
		'''
		self.set_all (self.OFF)
		self.latch_pulse ()

	def set_output_list (self, values):
		'''
			Set all outputs to the given values.
		'''
		assert (len (values) == self.__number_outputs)
		values.reverse () ## Need to write them backwards!
		for v in values:
			self.next (v)
		self.latch_pulse ()

	def set (self, **kwargs):
		'''
			Set all values based on the given
			kwargs, defaulting unspecified pins off.
		'''
		for i in range (self.__number_outputs):
			if not str (i) in kwargs.keys ():
				kwargs[str (i)] = self.OFF
		values = [a[1] for a in sorted (kwargs.items (), key=lambda x: x[0])]
		self.set_output_list (values)
