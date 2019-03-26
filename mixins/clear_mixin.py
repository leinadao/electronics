from ..exceptions import NoClearControl

class ClearMixin ():
	'''
		A mixin for adding clear control
		to an electrical component.
	'''
	ON = 1
	OFF = 0
	clear_active_low = True

	def __init__ (self, *args, **kwargs):
		'''
			Set up clear control.
		'''
		self.__clear_pin_id = kwargs.pop ('clear_pin_id', None)
		## Ensure clear is disabled if clear pin used:
		if self.controlling_clear_pin:
			GPIO.setup (self.__clear_pin_id, GPIO.OUT)
			self.__clear_value = self.OFF if self.clear_active_low else self.ON
		super ().__init__ (*args, **kwargs)

	@property
	def controlling_clear_pin (self):
		'''
			Return a boolean for whether
			the clear pin is controlled.
		'''
		return bool (self.__clear_pin_id)

	@property
	def clear_pin_on (self):
		'''
			Return a boolean for whether
			the enable pin is currently on.
		'''
		if not self.controlling_clear_pin:
			raise NoClearControl
		return self.__clear_value == self.ON

	def clear_off (self):
		'''
			Turn the enable pin off
			if it's not already.
		'''
		if not self.controlling_clear_pin:
			raise NoClearControl
		if self.clear_pin_on:
			GPIO.output (self.__clear_pin_id, GPIO.LOW)
			self.__clear_value = self.OFF

	def clear_on (self):
		'''
			Turn the enable pin on
			if it's not already.
		'''
		if not self.controlling_clear_pin:
			raise NoClearControl
		if not self.clear_pin_on:
			GPIO.output (self.__clear_pin_id, GPIO.HIGH)
			self.__clear_value = self.ON

	def clear (self):
		'''
			Pulse the clear pin.
		'''
		if not self.controlling_clear_pin:
			raise NoClearControl
		if self.clear_active_low:
			self.clear_off ()
			self.clear_on ()
		else:
			self.clear_on ()
			self.clear_off ()
