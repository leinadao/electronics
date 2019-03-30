from RPi import GPIO

from ..exceptions import NoClearControl

## Set the pin mode:
GPIO.setmode (GPIO.BCM)

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
		self._clear_pin_id = kwargs.pop ('clear_pin_id', None)
		## Ensure clear is disabled if clear pin used:
		if self.controlling_clear_pin:
			GPIO.setup (self._clear_pin_id, GPIO.OUT)
			self._clear_value = self.OFF if self.clear_active_low else self.ON
			self.no_clear ()
		super ().__init__ (*args, **kwargs)

	@property
	def controlling_clear_pin (self):
		'''
			Return a boolean for whether
			the clear pin is controlled.
		'''
		return bool (self._clear_pin_id)

	@property
	def clear_pin_on (self):
		'''
			Return a boolean for whether
			the enable pin is currently on.
		'''
		if not self.controlling_clear_pin:
			raise NoClearControl
		return self._clear_value == self.ON

	def clear_off (self):
		'''
			Turn the enable pin off
			if it's not already.
		'''
		if self.clear_pin_on:
			GPIO.output (self._clear_pin_id, GPIO.LOW)
			self._clear_value = self.OFF

	def clear_on (self):
		'''
			Turn the enable pin on
			if it's not already.
		'''
		if not self.clear_pin_on:
			GPIO.output (self._clear_pin_id, GPIO.HIGH)
			self._clear_value = self.ON

	def no_clear (self):
		'''
			Make sure clear is not active.
		'''
		if self.clear_active_low:
			self.clear_on ()
		else:
			self.clear_off ()

	def clear (self):
		'''
			Pulse the clear pin.
		'''
		if self.clear_active_low:
			self.clear_off ()
			self.clear_on ()
		else:
			self.clear_on ()
			self.clear_off ()
