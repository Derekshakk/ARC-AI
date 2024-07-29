# Imports
import threading
import time
import board
import busio
import cv2
import math
from PIL import Image
import adafruit_mlx90640
import numpy

i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)


frame = [0] * 768

avg_temp = 0
min_temp = 0
max_temp = 0

mlx = adafruit_mlx90640.MLX90640(i2c)

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
	
	
colormap = [0] * COLORDEPTH

for i in range(COLORDEPTH):
	colormap[i] = gradient(i, COLORDEPTH, heatmap)



while True:
	success = False
	while not success:
		try:
			mlx.getFrame(frame)
			success = True
		except ValueError:
			continue

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
	
	cv2_img = numpy.array(img)
	
	#print("max temp:", max(self.frame))
	#print("min temp:", min(self.frame))
	avg_temp = sum(frame)/len(frame)
	min_temp = min(frame)
	max_temp = max(frame)
	#print("average temp:", self.avg_temp)
	
	cv2.imshow("thermal_camera", cv2_img)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
		
	#print('thermal!!!')
	
	
cv2.destroyAllWindows()
print("Thermal Done")
