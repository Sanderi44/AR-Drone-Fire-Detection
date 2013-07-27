from cv2 import *
from SimpleCV import *

image = imread('fire5.jpeg')
b,g,r = split(image)
gb = compare(g,b,CMP_GT)
rg = compare(r,g,CMP_GT)
rrt = compare(r,230,CMP_GT)
rgb = bitwise_and(rg,gb)
rgbrt = bitwise_and(rgb,rrt)
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
R1234 = bitwise_and(R12,R34)

R = bitwise_and(R1234,rgbrt)
Ra = Image(R,cv2image=True)
blobs = Ra.findBlobs()
try:
	blobs[-1].draw()
	Ra.drawCircle((blobs[-1].centroid()),100,color = Color.RED)
except:
	pass
while(1):
	Ra.show()

