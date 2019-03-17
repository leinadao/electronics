from ..components import ShiftRegister

## Create a test shift register on pin 4 and 18:
test_shift_register = ShiftRegister (
	number_outputs = 16,
	data_pin_id = 4,
	clock_pin_id = 17,
	latch_pin_id = 18,
)
