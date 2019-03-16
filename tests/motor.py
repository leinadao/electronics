import time
import RPi.GPIO as GPIO
from random import random as random_random

## Set the pin mode:
GPIO.setmode(GPIO.BCM)

class TestMotor():
	'''
		A class for handling a test motor.
	'''
	STATUS_OFF = 0
	STATUS_ON = 1

	def __init__ (self, pin_id):
		'''
			A manager class for running
			a motor on a given GPIO pin.
		'''
		self.__pin_id = pin_id
		self.status = None
		GPIO.setup (self.__pin_id, GPIO.OUT)
		## Ensure it's initially turned off:
		self.off

	@property
	def off (self):
		'''
			Turn the motor off.
		'''
		GPIO.output (self.__pin_id, GPIO.LOW)
		self.status = self.STATUS_OFF

	@property
	def on (self):
		'''
			Turn the motor on.
		'''
		GPIO.output (self.__pin_id, GPIO.HIGH)
		self.status = self.STATUS_ON

	def pulse (self, seconds=1):
		'''
			Pulse the motor on then off.
		'''
		self.on
		time.sleep (seconds)
		self.off

	def pulse_random (self, iterations):
		'''
			Randomly pulse iteration times.
		'''
		for i in range (iterations):
			self.pulse (random_random ())
			time.sleep (random_random ())

## Create a test motor on pin 18:
TM1 = TestMotor (18)
TM2 = TestMotor (4)
