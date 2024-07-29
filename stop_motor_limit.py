from adafruit_motorkit import MotorKit
from adafruit_motor import stepper



from gpiozero import Button
import RPi.GPIO as GPIO
import time


import cv2
import time

import board
import busio


print("Thermal set up...")


'''
# Thermal Camera Set Up
'''

import threading

import math
from PIL import Image
import adafruit_mlx90640
import numpy

print("Thermal import done")


i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
print("i2c setup")


frame = [0] * 768

avg_temp = 0
min_temp = 0
max_temp = 0

mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ

# Set up mlx thermo camera
MINTEMP = 25.0  # low range of the sensor (deg C)
MAXTEMP = 45.0  # high range of the sensor (deg C)
COLORDEPTH = 1000  # how many color values we can have
INTERPOLATE = 10  # scale factor for final image

# the list of colors we can choose from
heatmap = (
	(0.0, (0, 0, 0)),
	(0.20, (0, 0, 0.5)),
	(0.40, (0, 0.5, 0)),
	(0.60, (0.5, 0, 0)),
	(0.80, (0.75, 0.75, 0)),
	(0.90, (1.0, 0.75, 0)),
	(1.00, (1.0, 1.0, 1.0)),
)

print("var setup")

	# some utility functions
def constrain(val, min_val, max_val):
	return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def gaussian(x, a, b, c, d=0):
	return a * math.exp(-((x - b) ** 2) / (2 * c**2)) + d


def gradient(x, width, cmap, spread=1):
	width = float(width)
	r = sum(
			gaussian(x, p[1][0], p[0] * width, width / (spread * len(cmap))) for p in cmap
	)
	g = sum(
			gaussian(x, p[1][1], p[0] * width, width / (spread * len(cmap))) for p in cmap
	)
	b = sum(
			gaussian(x, p[1][2], p[0] * width, width / (spread * len(cmap))) for p in cmap
	)
	r = int(constrain(r * 255, 0, 255))
	g = int(constrain(g * 255, 0, 255))
	b = int(constrain(b * 255, 0, 255))
	return r, g, b
	
	
print("def set up")

	
	
colormap = [0] * COLORDEPTH

for i in range(COLORDEPTH):
	colormap[i] = gradient(i, COLORDEPTH, heatmap)



proccessing_thermal_image = False
thermal_image = None


def showThermalImage():
	global proccessing_thermal_image
	if proccessing_thermal_image == False:
		if thermal_image is not None:
			cv2.imshow("ThermalImage", thermal_image)
		thread_obj = threading.Thread(target=showThermalImageThread)
		thread_obj.start()
		print("Processing New Thermal Image")
	else:
		print("already processing image New Thermal Image")
		
		

	

def showThermalImageThread():
	global proccessing_thermal_image, thermal_image
	proccessing_thermal_image = True
	try:
		mlx.getFrame(frame)
	except ValueError:
		proccessing_thermal_image = False
		print("ValueError Thermal Image")

	# create the image
	pixels = [0] * 768
	for i, pixel in enumerate(frame):
		coloridx = map_value(pixel, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1)
		coloridx = int(constrain(coloridx, 0, COLORDEPTH - 1))
		pixels[i] = colormap[coloridx]

	# save to file
	img = Image.new("RGB", (32, 24))
	img.putdata(pixels)
	img = img.transpose(Image.FLIP_TOP_BOTTOM)
	img = img.resize((32 * INTERPOLATE, 24 * INTERPOLATE), Image.BICUBIC)
	
	thermal_image = numpy.array(img)
	
	#print("max temp:", max(self.frame))
	#print("min temp:", min(self.frame))
	#avg_temp = sum(frame)/len(frame)
	#min_temp = min(frame)
	#max_temp = max(frame)
	#print("average temp:", self.avg_temp)
	
	#cv2.imshow("Thermal Image", cv2_img)
	proccessing_thermal_image = False

	print("Done Processing Thermal Image")


'''
# Camera set up
'''
print("camera setup")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()






cooking_time = 20 # in seconds - 300 seconds = 5 mins

linear_steps = 0
linear_steps_limit = 8000 # 8000 default
flip_step_location = 1000
limit_switch_safe_step = 100 # The top

cooking_steps = 1500 # 8000 or 7000 default
#cooking_steps = 7500 # 8000 or 7000 default


'''
Set up and start cameras
'''

#from camcamThread import CamThread
#camThread = CamThread()
#camThread.start()


#from thermal_camera_v2 import ThermalCameraV2
#i2c = busio.I2C(board.SCL, board.SDA, frequency=800_000)
#thermalCamera = ThermalCameraV2(i2c)
#thermalCamera.start()


'''
Motor Set Up

Motor 1 is the spinning handle driver


Motor 2 is the linear actuator
	backwards moves to the limit switch
	forward moves to the bottom
	1000 single steps == 250 mm
	10000 == 250mm == 25cm
	
'''

kit = MotorKit()

kit.stepper1.release()
kit.stepper2.release()

#exit()




'''
 Limit Switch Set  Up
 
 The limit switch button is set to GPIO Pin 23
 '''
 
limitswitch = Button(23)

print("Press the Limit Switch to confirm Set up...")
while True:
	if limitswitch.is_pressed:
		break

print("Limit Switch Confirmed")
time.sleep(1)

#camThread.pause = True

'''
Homing

Remember to move the linear actuator home, the direction is backwards
and is set up as motor 2
'''



print('Homing...')

i = 1
while True:
	if limitswitch.is_pressed:
		print("The Button was pressed")
		break

	#kit.stepper2.onestep(style=stepper.INTERLEAVE)

	#kit.stepper2.onestep(direction=stepper.BACKWARD)
	kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
	#kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
	#kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.INTERLEAVE)
#	kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
#	time.sleep(1)
	print(i)
	i = i + 1


linear_steps = 0

for i in range(100):
	linear_steps = linear_steps + 1
	kit.stepper2.onestep()

print('Homed\n')
linear_steps = 0



'''
Confirm start cooking

'''
#camThread.pause = False

start_word = 'cook'
print('Make sure the patties and the patties are setup correctly \n')
kit.stepper1.release()

while True:
	user_input = input('Type "{}" to start: '.format(start_word))
	if user_input.lower() == start_word:
		print("Starting Cooking!!")
		break
	else:
		print("Incorrect word. Please try again.")


    
kit.stepper1.onestep(style=stepper.MICROSTEP)
kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)


'''
Cooking 
linear_steps = 0
linear_steps_limit = 8000
flip_step_location = 1000
limit_switch_safe_step = 100
'''

def gotToTop():
	global linear_steps_limit, linear_steps, flip_step_location
	global limit_switch_safe_step, limitswitch, kit
	
	
	while True:
		if linear_steps <= limit_switch_safe_step:
			print("gotToTop - The Top was reaached")
			break

		elif limitswitch.is_pressed or linear_steps < limit_switch_safe_step:
			print("gotToTop - The Button was pressed")
			break

		kit.stepper2.onestep(direction=stepper.BACKWARD)
		linear_steps = linear_steps - 1
		#print('goToBottom - linear_steps:', linear_steps)


def goToBottom():
	global linear_steps_limit, linear_steps, flip_step_location
	global limit_switch_safe_step, limitswitch, kit
	
	
	while True:
		if linear_steps >= linear_steps_limit:
			print("goToBottom - The Bottom was reaached")
			break

		elif limitswitch.is_pressed or linear_steps < limit_switch_safe_step:
			print("goToBottom - The Button was pressed")
			break

		kit.stepper2.onestep()
		linear_steps = linear_steps + 1
		#print('goToBottom - linear_steps:', linear_steps)


def goToCooking():
	global linear_steps_limit, linear_steps, flip_step_location
	global limit_switch_safe_step, limitswitch, kit, cooking_steps
	
	
	while True:
		if linear_steps >= cooking_steps:
			print("goToCooking - Reached Cooking Height")
			break

		elif limitswitch.is_pressed and linear_steps > limit_switch_safe_step:
			print("goToCooking - The Button was pressed")
			break

		kit.stepper2.onestep()
		linear_steps = linear_steps + 1
		#print('goToCooking - linear_steps:', linear_steps)
		


def flipPatties():
	global linear_steps_limit, linear_steps, flip_step_location
	global limit_switch_safe_step, limitswitch, kit

	# got to a set spot
	
	while True:
	
		if linear_steps >= linear_steps_limit:
			# below the target, move backwards
			kit.stepper2.onestep(direction=stepper.BACKWARD)
			linear_steps = linear_steps - 1		
			print("flipPatties - The Bottom was reaached")
		elif limitswitch.is_pressed:
			# above the target, move forward
			kit.stepper2.onestep()
			linear_steps = linear_steps + 1
			print("flipPatties - The Top was reaached")	
		elif linear_steps > flip_step_location:
			# below the target, move backwards
			kit.stepper2.onestep(direction=stepper.BACKWARD)
			linear_steps = linear_steps - 1		
		elif linear_steps > flip_step_location:
			# above the target, move forward
			kit.stepper2.onestep()
			linear_steps = linear_steps + 1
		elif linear_steps == flip_step_location:
			# at position
			break	
		else:
			print('flipPatties - else?')

	# rotate basket
	## 200 * 16 is one full rotation
	for i in range(200 * 8):
		kit.stepper1.onestep(style=stepper.MICROSTEP)

	#kit.stepper1.onestep(style=stepper.DOUBLE)
	#kit.stepper1.onestep(style=stepper.DOUBLE)


def waitCooking(cookingDuration):
	start_time = time.time()
	end_time = start_time + cookingDuration
	
	while True:
		current_time = time.time()
		time_elapsed = current_time - start_time
		print("Time elapsed: ", time_elapsed, "/", cookingDuration)
		
		
		''' Camera '''
		ret, cam_frame = cap.read()
		if not ret:
			print("Error: Could not read frame.")
			break
		cv2.imshow('Camera Feed', cam_frame)
		
		
		''' Thermal Camera '''
		print(showThermalImage())
		
		if current_time >= end_time:
			break  # Exit the loop if the end time is reached

		# Introduce some delay to avoid excessive CPU usage
		cv2.waitKey(1)
		#while time.time() - current_time < 0.5:
		#	pass  # Wait until the interval has elapsed



'''
Cooking Time!!!

'''
#camThread.pause = True
goToCooking()

#camThread.pause = False
waitCooking(cooking_time)

#camThread.pause = True
flipPatties()


goToCooking()

#camThread.pause = False
waitCooking(cooking_time)

#camThread.pause = True
gotToTop()
#camThread.pause = False


'''
Clean Up
'''
start_word = 'fin'
print('Turn off the flames before removing the patties \n')

while True:
	user_input = input('Type "{}" to relase the motors: '.format(start_word))
	if user_input.lower() == start_word:
		print("Bon Appetit!!")
		break
	else:
		print("Incorrect word. Please try again.")


kit.stepper1.release()
kit.stepper2.release()



# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()


print('Camera Done')



print('Done')
