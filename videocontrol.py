#!/usr/bin/env python

import cv2
import pygame
import numpy
import libardrone


running = True
flying = False
path = 'tcp://192.168.1.1:5555'

drone = libardrone.ARDrone()
drone.reset()
drone.speed = 0.5
pygame.init()
W, H = 640, 360
hud_color = (255, 0, 0)
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
stream = cv2.VideoCapture(path)
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				drone.land()
				drone.reset()
			elif event.key == pygame.K_SPACE:
				if flying == False:
					drone.takeoff()
					flying = True
				else:
					drone.land()
					flying = False
			elif event.key == pygame.K_w:
				drone.move_forward()
			elif event.key == pygame.K_s:
				drone.move_backward()
			elif event.key == pygame.K_a:
				drone.move_left()
			elif event.key == pygame.K_d:
				drone.move_right()
			elif event.key == pygame.K_RIGHT:
				drone.turn_right()
			elif event.key == pygame.K_LEFT:
				drone.turn_left()
			elif event.key == pygame.K_UP:
				drone.move_up()
			elif event.key == pygame.K_DOWN:
				drone.move_down()
	if running == False:
		print "Shut Down"
		pygame.quit()
		drone.halt()
		break
	try:
		buff = stream.grab()
		imageyuv = stream.retrieve(buff)
		imagergb = cv2.cvtColor(imageyuv[1],cv2.COLOR_BGR2RGB)
		surface = pygame.image.frombuffer(imagergb, (W, H), 'RGB')
		bat = drone.navdata.get('battery', 0)
		screen.blit(surface, (0, 0))
		pygame.display.flip()
		clock.tick(50)
		pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
		f = pygame.font.Font(None, 20)
		hud = f.render('Battery: %i%%' % bat, True, hud_color)
		print bat
		screen.blit(hud,(10,10))
	except:
		print "Missed Frame"
		pass
pygame.quit()