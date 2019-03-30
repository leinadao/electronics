from RPi import GPIO

from ..exceptions import NoEnableControl

## Set the pin mode:
GPIO.setmode (GPIO.BCM)

class OutputEnableMixin ():
	'''
		A mixin for adding output enable
		control to an electrical component.
	'''
	ON = 1
	OFF = 0
	enable_active_low = True

	def __init__ (self, *args, **kwargs):
		'''
			Set up output enable control.
		'''
		self._enable_pin_id = kwargs.pop ('enable_pin_id', None)
		## Ensure output is enabled if enable pin used:
		if self.controlling_enable_pin:
			GPIO.setup (self._enable_pin_id, GPIO.OUT)
			self._enable_value = self.ON if self.enable_active_low else self.OFF
			self.enable ()
		super ().__init__ (*args, **kwargs)

	@property
	def controlling_enable_pin (self):
		'''
			Return a boolean for whether
			the output enable pin is controlled.
		'''
		return bool (self._enable_pin_id)

	@property
	def enable_pin_on (self):
		'''
			Return a boolean for whether
			the enable pin is currently on.
		'''
		if not self.controlling_enable_pin:
			raise NoEnableControl
		return self._enable_value == self.ON

	@property
	def enabled (self):
		'''
			Return a boolean for whether the shift
			register currently has output enabled.
		'''
		if self.enable_active_low:
			return not self.enable_pin_on
		return self.enable_pin_on

	def enable_off (self):
		'''
			Turn the enable pin off
			if it's not already.
		'''
		if self.enable_pin_on:
			GPIO.output (self._enable_pin_id, GPIO.LOW)
			self._enable_value = self.OFF

	def enable_on (self):
		'''
			Turn the enable pin on
			if it's not already.
		'''
		if not self.enable_pin_on:
			GPIO.output (self._enable_pin_id, GPIO.HIGH)
			self._enable_value = self.ON

	def enable (self):
		'''
			Enable output if its
			not already enabled.
		'''
		if not self.enabled:
			if self.enable_active_low:
				self.enable_off ()
			else:
				self.enable_on ()

	def disable (self):
		'''
			Disable output if its
			not already disabled.
		'''
		if self.enabled:
			if self.enable_active_low:
				self.enable_on ()
			else:
				self.enable_off ()
