from cv2 import *
from SimpleCV import *
import sys
import libardrone
import numpy

def rgbfilter(image):
	'''
	This is a color filter based on a method proposed in "Fire Detection Using Statistical
	Color Model in Video Sequences" by Turgay Celik, Hasan Demeril, Huseyin Ozkaramanli, Mustafa Uyguroglu

	This method uses the RGB color space and does three comparisons.
	The method returns true at any pixel that satisfies:
	red > green > blue
	red > red threshold (depends on amount of light in image)
	'''

	b,g,r = split(image)
	rt = 220
	gb = compare(g,b,CMP_GT)
	rg = compare(r,g,CMP_GT)
	rrt = compare(r,rt,CMP_GT)
	rgb = bitwise_and(rg,gb)
	
	return bitwise_and(rgb,rrt)

def rgbfilter2(image):
	""" 
	This is a simple threshold filter with experimental thresholds:
	r > rt (red threshold)
	g > gt (green threshold)
	b < bt (blue threshold)

	Night: rt = 0, gt = 100, bt = 140

	"""

	b,g,r = split(image)
	rt = 0
	gt = 100
	bt = 140
	ggt = compare(g,gt,CMP_GT)
	bbt = compare(b,bt,CMP_LT)
	rrt = compare(r,rt,CMP_GT)
	rgb = bitwise_and(ggt,bbt)
	
	return bitwise_and(rgb,rrt)

def labfilter(image):
	'''
	This is a filter based on a method proposed in "Fast and Efficient Method for Fire Detection
	Using Image Processing" by Turgay Celik

	This method uses the CIE L*a*b* color space and performs 4 bitwise filters
	The method returns true at any pixel that satisfies:
	L* > Lm* (mean of L* values)
	a* > am* (mean of a* values)
	b* > bm* (mean of b* values)
	b* > a*
	'''
	cieLab = cvtColor(image,COLOR_BGR2LAB)
	L,a,b = split(cieLab)
	Lm = mean(L)
	am = mean(a)
	bm = mean(b)
	R1 = compare(L,Lm,CMP_GT)
	R2 = compare(a,am,CMP_GT)
	R3 = compare(b,bm,CMP_GT)
	R4 = compare(b,a,CMP_GT)
	R12 = bitwise_and(R1,R2)
	R34 = bitwise_and(R3,R4)
	
	return bitwise_and(R12,R34)

def linearTime(theta):
	''' 
	Calibrated linear Equations for converting an angle to move time for 
	speed = 0.5 
	'''

	if theta > 0:
		''' Move Right '''
		t = 0.0201*theta - 0.1824
		if t <= 0:
			t = 0
	elif theta < 0:
		''' Move Left '''
		theta = -theta
		t = 0.0224*theta - 0.0891
		if t <= 0:
			t = 0
	else:
		t = 0

	print t
	return t

def quadTime(theta):
	''' 
	Calibrated quadratic Equations for converting an angle to move time for 
	speed = 0.5 
	'''

	if theta > 0:
		''' Move Right '''
		t = (theta*theta)*(0.00004) + 0.0126*theta + 0.0351
		if t <= 0:
			t = 0
	elif theta < 0:
		''' Move Left '''
		theta = -theta
		t = (theta*theta)*(0.00003) + 0.017*theta + 0.0682
		if t <= 0:
			t = 0
	else:
		t = 0

	print t
	return t

def findR(drone,cam,angle):
	# Grab and filter image 1
	img = filter(cam,1)
	fireblob1, firex1 = showImage(img,drone)
	
	# Move a specified angle
	t = quadTime(angle)
	drone.set_speed(0.5)
	drone.turn_right()
	time.sleep(t)
	drone.hover()

	# Grab and filter image 2
	time.sleep(2)
	img = filter(cam,1)
	fireblob2, firex2 = showImage(img,drone)

	# Calculate Pixel Distance
	pdist = firex2 - firex1

	# Find distance to object
	radius = pdist/(2*math.sin(math.radians((angle/2))))
	return radius

	

def turntofire(drone,cam,angle):
	# Calculate turn angle
	radius = findR(drone,cam,angle)
	img = filter(cam,1)
	fireblob, firex = showImage(img,drone)
	pixels = 320 - firex
	arg = pixels/radius
	print "arg: ",arg
	try:
		turnangle = math.degrees(math.asin(arg))
		print "turn angle: ",turnangle
	except:
		print "Problem"
	# # Turn the drone to the fire
	# t = quadtime(turnangle)
	# drone.set_speed(0.5)
	# drone.turn_right()
	# time.sleep(t)
	# drone.hover()






def manualmode(drone, display, flying):
	''' This is manual override mode '''

	# Key Numbers
	A = 97		# Turn Left
	S = 115		# Backward
	D = 100		# Turn Right
	W = 119		# Forward
	R = 114		# Reset Drone

	# Pause Time
	pause = 0.25


	if display.pressed[A] == 1 and flying == True:
		''' Turn Left by pressing A '''
		#t = linearTime(-22.5)
		t = quadTime(-10)
		drone.set_speed(0.5)
		drone.turn_left()
		time.sleep(t)
		drone.hover()

	elif display.pressed[D] == 1 and flying == True:
		'''Turn Right by pressing D '''
		#t = linearTime(22.5)
		t = quadTime(10)
		drone.set_speed(0.5)
		drone.turn_right()
		time.sleep(t)
		drone.hover()

	elif display.pressed[W] == 1 and flying == True:
		''' Move Forward by pressing W '''
		drone.set_speed(0.35)
		drone.move_forward()
		time.sleep(0.5)
		drone.hover()

	elif display.pressed[S] == 1 and flying == True:
		''' Move Backward by pressing S '''
		drone.set_speed(0.35)
		drone.move_backward()
		time.sleep(0.5)
		drone.hover()	

	return flying

def filter(camera,filt):
	''' 
	Choice of filters:
	filt = 0 : only RGB Filter
	filt = 1 : only cieLAB Filter
	filt = 2 : both filters
	filt = 3 : RGB Filter 2
	filt = 4 : Regular image
	 '''
	var,img = camera.read()

	if filt == 0:
		return Image(rgbfilter(img),cv2image=True)
	elif filt == 1:
		return Image(labfilter(img),cv2image=True)
	elif filt == 2:
		R1 = rgbfilter(img)
		R2 = labfilter(img)
		R = bitwise_and(R1,R2)
		return Image(R,cv2image=True)
	elif filt == 3:
		return Image(rgbfilter2(img),cv2image=True)
	elif filt == 4:
		return Image(cvtColor(img,COLOR_BGR2RGB),cv2image=True)
	else:
		print "Invalid Filter Number"
		return

def avgBlob(blobs):
	'''
	Find the average the of top 5 fire blobs
	'''
	blobs[0].draw()
	blobs[-1].draw()
	blobs[-2].draw()
	blobs[-3].draw()
	blobs[-4].draw()
	# If any of the blobs are outside of some range, exclude them
	# The more blobs in an area, the higher likelihood of a fire.		
	avgx = numpy.mean([blobs[0].x,blobs[-1].x,blobs[-2].x,blobs[-3].x,blobs[-4].x])
	avgy = numpy.mean([blobs[0].y,blobs[-1].y,blobs[-2].y,blobs[-3].y,blobs[-4].y])
	
	return avgx, avgy

def showImage(img,drone):
	""" 
	Performs blob detection and returns the blobs.  Also shows the image in a window.
	"""
	blobs = img.findBlobs()

	avgx, avgy = avgBlob(blobs)
	img.drawCircle((avgx,avgy),100,color = Color.RED)
	position = "X: " + str(avgx) + ", Y: " + str(avgy)
		
	img.drawText(position,50,50,color=Color.GREEN)

	if drone.navdata.get('drone_state',dict()).get('emergency_mask',1) == 1:
		img.drawText('Emergency Mode',50,50,color=Color.RED)
	img.show()
	return blobs, avgx

def main():
	# Drone setup
	print "Connecting to Drone"	
	try:
		drone = libardrone.ARDrone()
		go = True
		print "Connected to Drone"
	except:
		print "Cannot Connect"
		go = False
	#drone.reset()
	
	# Video Setup
	path = 'tcp://192.168.1.1:5555'
	cam = VideoCapture(path)
	if cam.isOpened():
		print "Video is Connected"
		go = True
	else:
		print "Video is not Connected"
		go = False

	# Variables
	print "Manual On"
	manual = True
	testangle = -15

	# Key Numbers
	Q = 113		# Quit
	R = 114		# Reset
	M = 109		# Manual Mode On/Off
	B = 98		# Display Battery in Terminal
	space = 32	# Takeoff/Land

	# Pygame Display
	d = Display()
	img = filter(cam,1)
	img.show()
	#print img.size()
	# Is the drone flying?
	flying = False
	
	if go == True:
		while not d.isDone():

			if d.pressed[102]:
				# Press F to find Distance to object
				turntofire(drone,cam,testangle)
			
			#print d.checkEvents()
			elif display.pressed[space] == 1:
				''' Takeoff/Land by pressing Spacebar '''
				if flying == True:
					drone.land()
					flying = False
				else:
					drone.takeoff()
					flying = True
				time.sleep(0.5)

			elif d.pressed[Q] == 1:
				# Press Q to Quit
				print "Exiting"
				d.done = True

			elif d.pressed[R] == 1:
				# Press R to Reset (Doesn't Seem to Work)
				drone.reset()
				print 'Reset'
				time.sleep(0.1)

			elif d.pressed[M] == 1:
				# Press M to turn Manual Mode on and off
				if manual == True:
					manual = False
					print "Manual Off"
				else:
					manual = True
					print "Manual On"
				time.sleep(0.5)

			elif d.pressed[B] == 1:
				# Press B for Battery Status
				print 'Battery: %',drone.navdata.get(0, dict()).get('battery', 0)

			if manual == True:
				flying = manualmode(drone,d,flying)



	# Quit Pygame and Halt Drone
	d.quit()
	drone.land()
	drone.halt()

if __name__ == "__main__":
    sys.exit(main())