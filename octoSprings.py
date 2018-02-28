
import math
import random
import pygame

(width, height) = (800, 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('OctoSprings')


numSegs = 20
segTall = 50
segWide = 25
dampCons = 0.025
shinkMod = 0.95

def addVectors((angle1, length1), (angle2, length2)):
	""" Returns the sum of two vectors """
	
	x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
	y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
	
	angle  = 0.5 * math.pi - math.atan2(y, x)
	length = math.hypot(x, y)

	return (angle, length)

def calcDist(Point1,Point2):
	x1 = Point1.x
	y1 = Point1.y
	x2 = Point2.x
	y2 = Point2.y

	d = math.sqrt((x1-x2)**2+(y1-y2)**2)

	return d

class MassPoint:
	def __init__(self,(x, y), size=3, mass=3):
		self.x = x
		self.y = y
		self.size = size
		self.colour = (0, 0, 255)
		self.speed = 0
		self.angle = 0
		self.mass = mass

	def move(self):
		""" Update position based on speed, angle """

		self.x += math.sin(self.angle) * self.speed
		self.y -= math.cos(self.angle) * self.speed

	def accelerate(self, vector):
		""" Change angle and speed by a given vector """		
		(self.angle, self.speed) = addVectors((self.angle, self.speed), vector)


class Spring:
	def __init__(self, p1, p2, length=segWide, strength=1):
		self.p1 = p1
		self.p2 = p2
		self.length = length
		self.origLength = length
		self.strength = strength
	
	def update(self):
		dx = self.p1.x - self.p2.x
		dy = self.p1.y - self.p2.y
		dist = math.hypot(dx, dy)
		theta = math.atan2(dy, dx)
		force = (self.length - dist) * self.strength
		
		self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
		self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))

		dampAmount = (force*(1-math.exp(-dampCons)))

		self.length -= dampAmount

	def restore(self):
		if self.length < self.origLength:
			self.length += 0.3


topY = height/2 - segTall/2
bottomY = height/2 + segTall/2

anchors = [MassPoint((0,topY),size =5),MassPoint((0,bottomY),size = 5)]
points = []
springs = []

for x in range(numSegs):
	newSegLen = (segTall/2)*(shinkMod**(x+1))

	topY = height/2 - newSegLen
	bottomY = height/2 + newSegLen

	newUpPoint = MassPoint((segWide*(x+1),topY))
	newDownPoint = MassPoint((segWide*(x+1),bottomY))
	if x == 0:
		oldUpPoint = anchors[0]
		oldDownPoint = anchors[1]
	else:
		oldUpPoint = points[-2]
		oldDownPoint = points[-1]
	
	upSpring = Spring(oldUpPoint,newUpPoint)
	midSpring = Spring(newUpPoint,newDownPoint,length = bottomY-topY)
	downSpring = Spring(oldDownPoint,newDownPoint)

	top2botSpring = Spring(oldUpPoint,newDownPoint,length = calcDist(oldUpPoint,newDownPoint),strength=3)
	bot2tobSpring = Spring(oldDownPoint,newUpPoint,length = calcDist(oldDownPoint,newUpPoint),strength=3)

	points.append(newUpPoint)
	points.append(newDownPoint)
	springs.append(upSpring)
	springs.append(midSpring)
	springs.append(downSpring)
	springs.append(top2botSpring)
	springs.append(bot2tobSpring)


running = True
moveAmount = -0.5
minLen = segWide/2

upKeys = [pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_r,pygame.K_t,pygame.K_y,pygame.K_u,pygame.K_i,pygame.K_o,pygame.K_p]
downKeys = [pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_j,pygame.K_k,pygame.K_l,pygame.K_SEMICOLON]

while running:
	keys = pygame.key.get_pressed()

	for i in range(10):
	 	if keys[upKeys[i]]:
	 		if(springs[i*5].length > minLen):
	 			springs[i*5].length += moveAmount
	 	else:
	 		springs[i*5].restore()

	 	if keys[downKeys[i]]:
	 		if(springs[i*5+2].length > minLen):
	 			springs[i*5+2].length += moveAmount
	 	else:
	 		springs[i*5+2].restore()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		 	running = False


	screen.fill((255,255,255))

	for s in springs:
		s.update()
		pygame.draw.aaline(screen, (0,0,0), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))

	for p in points:
		p.move()
		pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)

	for a in anchors:
		pygame.draw.circle(screen, a.colour, (int(a.x), int(a.y)), a.size, 0)

	pygame.display.flip()






