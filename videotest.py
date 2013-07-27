import cv2
import numpy
import libardrone



running = True
flying = False
path = 'tcp://192.168.1.1:5555'
go = False
nc = 0
drone = libardrone.ARDrone()
drone.reset()
drone.speed = 0.1
W, H = 640, 360
rt = 240

stream = cv2.VideoCapture(path)
while running:
	try:
		buff = stream.grab()
		imageyuv = stream.retrieve(buff)
		imagergb = cv2.cvtColor(imageyuv[1],cv2.COLOR_BGR2RGB)
		imagehsv = cv2.cvtColor(imagergb,cv2.COLOR_RGB2HSV)
		#imagegray = cv2.cvtColor(imagergb,cv2.COLOR_RGB2GRAY)
		h,s,v = cv2.split(imagehsv)
		r,g,b = cv2.split(imagergb)
		gb = cv2.compare(g,b,cv2.CMP_GT)
		rg = cv2.compare(r,g,cv2.CMP_GT)
		rrt = cv2.compare(r,rt,cv2.CMP_GT)
		rgb = cv2.compare(rg,gb,cv2.CMP_EQ)
		rgbrt = cv2.compare(rgb,rrt,cv2.CMP_EQ)
		sat = cv2.compare(s,50,cv2.CMP_LT)
		rgbrts = cv2.compare(sat,rgbrt,cv2.CMP_LT)
		#cv2.imshow("RGB",imagergb)
		cv2.imshow("Threshold",rgbrt)
		cv2.imshow("SAT",sat)
		if go == True:
			change = rgbrt - lastimg
			#cv2.imshow("Change",change)
		nc = 0
		lastimg = rgbrt
		go = True
	except:
		print "Missed Frame"
		nc = nc + 1
		if nc > 5:
			print "Not Connected"
			break
	c = cv2.waitKey(5)
	

cv2.destroyAllWindows()
