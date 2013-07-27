from cv2 import *
from SimpleCV import *
import numpy

mov = 'IMG_0175.mov'
cam = VirtualCamera(mov,'video')

def rgbfilter2(image):
	b,g,r = split(image)
	rt = 0
	gt = 100
	bt = 140
	ggt = compare(g,gt,CMP_GT)
	bbt = compare(b,bt,CMP_LT)
	rrt = compare(r,rt,CMP_GT)
	rgb = bitwise_and(ggt,bbt)
	return bitwise_and(rgb,rrt)


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
	rt = 100
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
i = 0
while True:
	image = cam.getImage()
	img = image.getNumpy()
	R1 = rgbfilter2(img)
	R2 = labfilter(img)
	R = bitwise_and(R1,R2)
	Ra = Image(R1).bilateralFilter(diameter=10,sigmaColor=50,sigmaSpace=40, grayscale=True)
	blobs = Ra.findBlobs()

	try:
		blobs[0].draw()
		blobs[-1].draw()
		blobs[-2].draw()
		blobs[-3].draw()
		blobs[-4].draw()

		# If any of the blobs are outside of some range, exclude them
		# The more blobs in an area, the higher likelihood of a fire.		
		avgx = numpy.mean([blobs[0].x,blobs[-1].x,blobs[-2].x,blobs[-3].x,blobs[-4].x])
		avgy = numpy.mean([blobs[0].y,blobs[-1].y,blobs[-2].y,blobs[-3].y,blobs[-4].y])
		Ra.drawCircle((avgx,avgy),100,color = Color.RED)
		position = "X: " + str(avgx) + ", Y: " + str(avgy)
		
		Ra.drawText( position,50,50,color=Color.GREEN)

	except:
		pass

	
	Ra.show()
	time.sleep(0.1)
	if i == 10:
		image.show()
		time.sleep(0.5)
		i = 0
	else:
		i = i+1