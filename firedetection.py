from cv2 import *
from SimpleCV import *
import sys
import libardrone


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

def manualmode(drone, display, flying):
	''' This is manual override mode '''

	# Key Numbers
	space = 32	# Takeoff/Land
	A = 97		# Turn Left
	S = 115		# Backward
	D = 100		# Turn Right
	W = 119		# Forward
	R = 114		# Reset Drone

	# Pause Time
	pause = 0.1

	if display.pressed[space] == 1:
		if flying == True:
			drone.land()
			flying = False
		else:
			drone.takeoff()
			flying = True
		time.sleep(pause)

	elif display.pressed[A] == 1 and flying == True:
		drone.set_speed(0.35)
		drone.turn_left()
		time.sleep(0.1)
		drone.hover()


	elif display.pressed[D] == 1 and flying == True:
		drone.set_speed(0.35)
		drone.turn_right()
		time.sleep(0.1)
		drone.hover()

	elif display.pressed[W] == 1 and flying == True:
		drone.set_speed(0.2)
		drone.move_forward()
		time.sleep(0.25)
		drone.hover()

	elif display.pressed[S] == 1 and flying == True:
		drone.set_speed(0.2)
		drone.move_backward()
		time.sleep(0.25)
		drone.hover()	

	return flying

def filter(camera,filt):
	''' 
	Choice of filters to use:
	filt = 0 : only RGB Filter
	filt = 1 : only cieLAB Filter
	filt = 2 : both filters
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
	else:
		print "Invalid Filter Number"
		return

def showImage(img,drone):
	blobs = img.findBlobs()
	try:
		blobs[-1].draw()
		img.drawCircle((blobs[-1].centroid()),100,color = Color.RED)
	except:
		pass
	if drone.navdata.get('drone_state',dict()).get('emergency_mask',1) == 1:
		img.drawText('Emergency Mode',50,50,color=Color.RED)
	img.show()
	return blobs

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
	drone.set_speed(0.2)
	
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

	# Pygame Display
	d = Display()

	# Is the drone flying?
	flying = False
	
	if go == True:
		while not d.isDone():
			img = filter(cam,2)
			fireblob = showImage(img,drone)

			#print d.checkEvents()
			if d.pressed[113] == 1:
				# Press Q to Quit
				print "Exiting"
				d.done = True

			elif d.pressed[114] == 1:
				# Press R to Reset (Doesn't Seem to Work)
				drone.reset()
				print 'Reset'
				time.sleep(0.1)

			elif d.pressed[109] == 1:
				# Press M to turn Manual Mode on and off
				if manual == True:
					manual = False
					print "Manual Off"
				else:
					manual = True
					print "Manual On"
				time.sleep(0.5)

			elif d.pressed[98] == 1:
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