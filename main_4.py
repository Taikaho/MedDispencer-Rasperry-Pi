# Import GPIO to control Raspberry PI pins
# Import time and datetime to add delay and date to change current date
# Import python codes change_time and create_lod_entry (miksi?)

import RPi.GPIO as GPIO
import time
from datetime import datetime
import change_time_4
from database_functions_4 import create_log_entry

# Define RaspberryPI pins for IR-sensor, buzzer and LED-light
# Set pins as INPUT or OUTPUT
# GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

sensor = 6
buzzer = 26
led = 16
this_day = 99
sleep = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.setup(led, GPIO.OUT)

GPIO.output(buzzer, 0)
GPIO.output(led, 0)

# Define RaspberryPI pins for stepmotor
# Set them as OUTPUT with for-loop
ControlPin = [17, 27, 22, 5]

for pin in ControlPin:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)


# Timer-function
# Owner MinttuS, modified by KariE
# Current time and set times are modified to epoch and integer previously
# These are now easier to compare in if-loop. If times are same, rotatingMotor-function is called.
# Loop waits set time so object have enough time to move close to the sensor.
# irSensor-fucntion is called
def timer(current_epoch):
	for epoch in epochs:
		""" print(current_epoch) """
		if current_epoch == epoch:
			print("Tavoiteaika", nyt1.strftime("%Y-%m-%d %H:%M"), "on saavutettu")
			rotating_motor()
			time.sleep(sleep)
			status = ir_sensor()
			time_GMT = nyt1.strftime("%Y-%m-%d %H:%M")
			entry = (status, epoch, time_GMT)
			create_log_entry(entry)

# Motor-function
# Owner Taikaho
# Set stepmotors step sequence as array
# In for-loop step motor coils are turned on one by one, which rotates motor
def rotating_motor():
	seq = [
		[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1],
		[1,0,0,1]
	]

	for i in range(50):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(ControlPin[pin], seq[halfstep][pin])
			time.sleep(0.001)
		

# IR-sensor-function
# Owner Taikaho
# If IR-sensor detects object, it sets LOW and buzzer and LED sets HIGH		
def ir_sensor():
	if GPIO.input(sensor) == 1:
		return "Lääkettä ei annosteltu"
	
	now_epoch = time.time()

	while True:
		if GPIO.input(sensor) == 0:
			GPIO.output(buzzer,1)
			GPIO.output(led, 1)
			while GPIO.input(sensor) == 0:
				time.sleep(0.2)
			if time.time() - now_epoch == 1800:
				return "Lääkettä ei otettu"
		else:
			GPIO.output(buzzer, 0)
			GPIO.output(led, 0)
			return "Lääke annosteltu"

# Main-loop
# Owner MinttuS, modified by KariE
# If-sentence, if nyt1 is different from this_day, new epoch-times are returnes from change_times file
# this_day is set to be same with nyt1, so if-sentence doesnät go through every second
# If-sentence is used, so at midnight nyt1 changes to next date and next day epoch-times are returned

# Define current epoch-time from computer system with time.time()
# Rounded and changed to int-variable
# Call and go through timer-function, sleep 1 second

while True:
	nyt1 = datetime.now()

	if int(nyt1.strftime("%d")) != this_day:
		epochs = change_time_4.change_dispense_times

		this_day = int(nyt1.strftime("%d"))

	seconds = time.time()
	current_epoch = round(seconds)
		
	timer(current_epoch)
	time.sleep(1)

GPIO.cleanup()
