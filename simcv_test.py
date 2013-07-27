from cv2 import *
from SimpleCV import *



path = 'tcp://192.168.1.1:5555'

cam = VideoCapture(path)
rt = 230
gt = 150
bt = 90
firstpass = False
while (1):
	var,img = cam.read()
	r,g,b = split(img)
	gb = compare(g,b,CMP_GT)
	rg = compare(r,g,CMP_GT)
	#rrt = compare(r,rt,CMP_GT)
	#ggt = compare(g,gt,CMP_GT)
	#bbt = compare(b,bt,CMP_LT)
	#rgt = rrt*ggt
	#rgbt = rgt*bbt
	rgb = bitwise_and(rg,gb)
	#rgbrt = bitwise_and(rgb,rgbt)
	mask = Image(rgb, cv2image=True)
	
	blobs = mask.findBlobs()
	try:
		if blobs[-1].area() > 1000:
			blobs[-1].draw()
			mask.drawCircle((blobs[-1].centroid()),10,color = Color.BLUE)
		
	except:
		pass
	mask.show()
	waitKey(200)