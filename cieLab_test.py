from cv2 import *
from SimpleCV import *



path = 'tcp://192.168.1.1:5555'

cam = VideoCapture(path)

firstpass = False
while (1):
	var,img = cam.read()
	cieLab = cvtColor(img,COLOR_BGR2LAB)
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
	R1234 = bitwise_and(R12,R34)

	mask = Image(R1234, cv2image=True)
	smoothmask = mask.smooth()
	blobs = smoothmask.findBlobs(5)

	try:
		if blobs[-1].area() > 1000:
			blobs[-1].draw()
			smoothmask.drawCircle((blobs[-1].centroid()),10,color = Color.BLUE)
	except:
		pass
	smoothmask.show()
	waitKey(200)