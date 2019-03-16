###~~~MiniPi - Raspberry Pi Car Control - Daniel Osborne 2017~~~###

'''A module for controlling a model car via a Raspberry Pi Zero.'''

##Import required modules:
import RPi.GPIO as GPIO
#from msvcrt import getch ##Windows
from getch import getch ##Linux
from threading import Thread
import time

##Define module variables:
developerMode = True #temp - default changed later
slowForSeconds = 5

##Pin dictionary stores GPIO pin numbers against pin names so that pin numbers need only be configured here:
pinDictionary = {
    'forward': 17,
    'backward': 18,
    'left': 23,
    'right': 22,
}

##Status object tracks current operation desired:
status = {
    'running': True,
    'drive': None,
    'slowingStarted': None,
    'steering': None,
    'indicatorLights': None,
    'mainLights': None,
    'brakeLights': False,
    'reversingLights': False,
    'parkingLights': False,
    'horn': False,
    'sound': False,
}

##Define output functions:
def print_developer(message):
	'''A function to print a message if in developer mode.'''
	global developerMode
	if developerMode:
		print(message)

##Define pin control functions:
def configure_pin(pinDictionaryKey):
	'''A function to configure a GPIO pin.'''
	GPIO.setup(pinDictionary[pinDictionaryKey], GPIO.OUT)

def unconfigure_pins():
	'''A function to unconfigure the GPIO pins.'''
	GPIO.cleanup()

def control_pin(pinDictionaryKey,value):
	'''A function to control a GPIO pin.'''
	assert (value or not value)
	GPIO.output(pinDictionary[pinDictionaryKey], value)
	print("Set pin " + str(pinDictionary[pinDictionaryKey]) + " to " + str(value))

def start_up():
	'''A function to handle the start up of the program and initialise all of the required pins.'''
	GPIO.setmode(GPIO.BCM)
	for eachKey in pinDictionary.keys():
		configure_pin(eachKey)
		control_pin(eachKey, False)

##Define control functions:
def slowing_control():
	'''A function to control drive motor slowing.'''
	global status
	if (status['slowingStarted'] == None):
		return False
	elif ((time.time() - status['slowingStarted']) >= slowForSeconds):
		status['slowingStarted'] = None
		return False
	else:
		print_developer("Action Cancelled: Still slowing...")
		status['drive'] = 'slowing'
		return True

def drive_control():
	'''A function to enact changes to the status of the drive.'''
	global status
	if status['running']:
		if not slowing_control():
			##Control drive:
			if (status['drive'] == None):
				control_pin('forward',False)
				control_pin('backward',False)
			elif (status['drive'] == 'slowing'):
				control_pin('forward',True)
				control_pin('backward',True)
				status['slowingStarted'] = time.time()
			elif (status['drive'] == 'forward'):
				control_pin('backward',False)
				control_pin('forward',True)
			elif (status['drive'] == 'backward'):
				control_pin('forward',False)
				control_pin('backward',True)
			else:
				print("Warning: Unknown driving status!")

def steering_control():
	'''A function to enact changes to the status of the steering.'''
	global status
	if status['running']:
		##Control steering:
		if (status['steering'] == None):
			control_pin('left',False)
			control_pin('right',False)
		elif (status['steering'] == 'left'):
			control_pin('right',False)
			control_pin('left',True)
		elif (status['steering'] == 'right'):
			control_pin('left',False)
			control_pin('right',True)
		else:
			print("Warning: Unknown steering status!")

def lights_control():
	'''A function to enact changes to the status of the lights.'''
	pass

def sound_control():
	'''A function to enact changes to the status of the sound.'''
	pass

##Define status setting functions:
def forward_pressed():
	'''A function to handle the event of a forward button being pressed.'''
	global status
	if (status['drive'] == 'forward'):
		status['drive'] = None
		print_developer("No longer going forward...")
	elif (status['drive'] == 'backward'):
		status['drive'] = 'slowing'
		print_developer("Now slowing...")
	elif (status['drive'] == 'slowing'):
		status['drive'] = 'forward'
		print_developer("Trying to go forward...")
	elif (status['drive'] == None):
		status['drive'] = 'forward'
		print_developer("Now going forward...")

def backward_pressed():
	'''A function to handle the event of a backward button being pressed.'''
	global status
	if (status['drive'] == 'backward'):
		status['drive'] = None
		print_developer("No longer going backward...")
	elif (status['drive'] == 'forward'):
		status['drive'] = 'slowing'
		print_developer("Now slowing...")
	elif (status['drive'] == 'slowing'):
		status['drive'] = 'backward'
		print_developer("Trying to go backward...")
	elif (status['drive'] == None):
		status['drive'] = 'backward'
		print_developer("Now going backward...")

def left_pressed():
	'''A function to handle the event of a left button being pressed.'''
	global status
	if (status['steering'] == 'left'):
		status['steering'] = None
		print_developer("Now going straight...")
	elif ((status['steering'] == 'right') or (status['steering'] == None)):
		status['steering'] = 'left'
		print_developer("Now turning left...")

def right_pressed():
	'''A function to handle the event of a right button being pressed.'''
	global status
	if (status['steering'] == 'right'):
		status['steering'] = None
		print_developer("Now going straight...")
	elif ((status['steering'] == 'left') or (status['steering'] == None)):
		status['steering'] = 'right'
		print_developer("Now turning right...")

def stop_all():
	'''A function to handle a spacebar pressed 'stop-all' event.'''
	global status
	if (status['drive'] in ['forward','backward']): #Prevents emergency stop cancelling slowing countdown.
		status['drive'] = None
	status['steering'] = None
	status['lights'] = None
	print_developer("Emergency stop performed!")

def left_indicator_pressed():
	'''A function to handle the event of a left indicator button being pressed.'''
	global status
	if (status['indicatorLights'] == 'left'):
		status['indicatorLights'] = None
		print_developer("Left indicator cancelled...")
	elif (status['indicatorLights'] in ['right',None,'hazard']):
		status['indicatorLights'] = 'left'
		print_developer("Now indicating left...")

def right_indicator_pressed():
	'''A function to handle the event of a right indicator button being pressed.'''
	global status
	if (status['indicatorLights'] == 'right'):
		status['indicatorLights'] = None
		print_developer("Right indicator cancelled...")
	elif (status['indicatorLights'] in ['left',None,'hazard']):
		status['indicatorLights'] = 'right'
		print_developer("Now indicating right...")

def hazards_pressed():
	'''A function to handle the event of a hazards button being pressed.'''
	global status
	if (status['indicatorLights'] == 'hazard'):
		status['indicatorLights'] = None
		print_developer("Hazard lights cancelled...")
	else:
		status['indicatorLights'] = 'hazard'
		print_developer("Hazard warning lights set...")

def toggle_parking_lights():
	'''A function to toggle the parking lights on / off.'''
	global status
	if (status['parkingLights']):
		status['parkingLights'] = False
		print_developer("Parking lights turned off...")
	else:
		status['parkingLights'] = True
		print_developer("Parking lights turned on...")

def dipped_beam_pressed():
	'''A function to handle the event of a dipped beam button being pressed.'''
	global status
	if (status['mainLights'] == 'dipped'):
		status['mainLights'] = None
		print_developer("Dipped beam lights turned off...")
	elif (status['mainLights'] in ['main',None]):
		status['mainLights'] = 'dipped'
		print_developer("Dipped beam lights turned on...")

def main_beam_pressed():
	'''A function to handle the event of a main beam button being pressed.'''
	global status
	if (status['mainLights'] == 'main'):
		status['mainLights'] = None
		print_developer("Main beam lights turned off...")
	elif (status['mainLights'] in ['dipped',None]):
		status['mainLights'] = 'main'
		print_developer("Main beam lights turned on...")

def toggle_horn():
	'''A function to toggle the horn on / off.'''
	global status
	if (status['horn']):
		status['horn'] = False
		print_developer("Horn turned off...")
	else:
		status['horn'] = True
		print_developer("Horn turned on...")

def toggle_sound():
	'''A function to toggle the sound on / off.'''
	global status
	if (status['sound']):
		status['sound'] = False
		print_developer("Sound turned off...")
	else:
		status['sound'] = True
		print_developer("Sound turned on...")

def toggle_developer_mode():
	'''A function to toggle developer mode on / off.'''
	global developerMode
	if developerMode:
		developerMode = False
		print("Developer mode turned off...")
	else:
		developerMode = True
		print("Developer mode turned on...")

def action_control_key(key):
	'''A function to action a controlling key press.'''
	if (key == 32):
		stop_all()
		drive_control()
		steering_control()
		lights_control()
		sound_control()
	elif (key in [72,119]): ##Up arrow and 'w'
		forward_pressed()
		drive_control()
	elif (key in [80,115]): ##Down arrow and 's'
		backward_pressed()
		drive_control()
	elif (key in [75,97]): ##Left arrow and 'a'
		left_pressed()
		steering_control()
	elif (key in [77,100]): ##Right arrow and 'd'
		right_pressed()
		steering_control()
	elif (key == 108): ##'l'
		left_indicator_pressed()
		lights_control()
	elif (key == 114): ##'r'
		right_indicator_pressed()
		lights_control()
	elif (key == 35):
		hazards_pressed()
		lights_control()
	elif (key == 104): ##'#'
		toggle_horn()
		sound_control()
	elif (key == 113): ##'q'
		toggle_sound()
		sound_control()
	elif (key == 63): ##'?'
		toggle_developer_mode()
	elif (key == 112): ##'p'
		toggle_parking_lights()
		lights_control()
	elif (key == 110): ##'n'
		dipped_beam_pressed()
		lights_control()
	elif (key == 109): ##'m'
		main_beam_pressed()
		lights_control()

##Define input functions:
def watch_keyboard():
	'''A function to monitor the keyboard for key-press events and act upon them.'''
	global status
	while status['running']:
		watching = True
		while watching:
			key = ord(getch())
			if (key == 27): ##Escape.
				print("Are you sure you want to exit? Press 'Y' to confirm or any other key to cancel: ")
				key = ord(getch())
				if (key == 89):
					watching = False
					stop_all()
					drive_control()
					steering_control()
					lights_control()
					status['running'] = False
					print("Exiting...")
					break
			elif (key == 224): ##Special keys
				key = ord(getch())
				##print_developer(key)
				action_control_key(key)
			else:
				##print_developer(key)
				action_control_key(key)
			key = None

##Define running code:
if __name__ == '__main__':
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print("MiniPi starting up!..")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

	##Configure the required pins into the required format:
	unconfigure_pins() ##As some boot in the wrong configuration or already loaded.
	start_up()
	##Start listener thread - Reads key input and uses this to change the status list:
	watch_keyboard()
	##Unconfigure pins for complete exit.
	unconfigure_pins()
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print("Shutdown complete!")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

#temp - need lights
#temp - need sound
#temp - need to activate and deactive brake lights for slowing. - in light control thread -> look for 'slowing' status
#temp - need to activate and deactive reversing lights for reversing - in light control thread -> look for 'backward' status
#temp - add auto cancelling of indicator after turning!
#temp - is shutdown waiting long enough?
#temp - key bindings - could have text file to save and ability to load different 'users'.
#temp - are slowing and off set the correct way around in drive_control?
