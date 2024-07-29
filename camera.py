
# Imports
import cv2
import time

import board

'''
# Camera set up
'''

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
    
    
    
'''
The Loop
'''
# Keep reading frames from the camera
while True:
	''' Camera '''
	ret, cam_frame = cap.read()
	if not ret:
		print("Error: Could not read frame.")
		break
	cv2.imshow('Camera Feed', cam_frame)




    # Check for the 'q' key to quit the loop
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
        
       
# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()


print('Camera Done')
