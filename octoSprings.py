#Made by Ben Tidswell
#For BIOL 311
#Contact at betidswell@vassar.edu

#Inspired by this paper:
#Yekutieli, Y., Sagiv-Zohar, R., Aharonov, R., Engel, Y., Hochner, B., & Flash, T. (2005).
#	 Dynamic model of the octopus arm. I. Biomechanics of the octopus reaching movement. 
#	 Journal of Neurophysiology, 94(2), 1443-1458.

import math
import random
import pygame

#Sets up the pygame screen
pygame.init()
(width, height) = (800, 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('OctoSprings')
font = pygame.font.Font(None, 40)

#These set global varibles
#These first 4 set the geometry of the arm
#shrink mod makes the distal area thinner 
#than the proximal 
numSegs = 20
segTall = 50
segWide = 25
shinkMod = 0.95

#This changes amount that springs are dampened
#This value is good so it moves around some after but not too much.
#Currently it stays in place after moving and is not effected by gravity 
# or the like
dampCons = 0.1

def makeTarget():
	#Makes a target that is touchable by the arm
	x = random.randint(200,450)
	if(random.random() > 0.5):
		y = random.randint(150,250)
	else:
		y = random.randint(350,450)
	return(x,y)

def addVectors((angle1, length1), (angle2, length2)):
	#Returns the sum of two vectors
	
	x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
	y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
	
	angle  = 0.5 * math.pi - math.atan2(y, x)
	length = math.hypot(x, y)

	return (angle, length)

def calcDist(Point1,Point2):
	#calculates the distance between 2 points

	x1 = Point1.x
	y1 = Point1.y
	x2 = Point2.x
	y2 = Point2.y

	d = math.sqrt((x1-x2)**2+(y1-y2)**2)

	return d

def gotTarget(target,tip):
	tipXs = []
	tipYs = []

	targetX = target[0]
	targetY = target[1]

	for t in tip:
		tipXs.append(t.x)
		tipYs.append(t.y)

	maxX = max(tipXs)
	minX = min(tipXs)
	maxY = max(tipYs)
	minY = min(tipYs)

	if (minX < targetX < maxX) and (minY < targetY < maxY):
		return True
	else:
		return False

class MassPoint:
	#This class defines the mass point objects that define the arm
	def __init__(self,(x, y), size=3, mass=3):
		self.x = x
		self.y = y
		self.size = size
		self.colour = (0, 0, 255)
		self.speed = 0
		self.angle = 0
		self.mass = mass

	def move(self):
		#Update position based on speed, angle

		self.x += math.sin(self.angle) * self.speed
		self.y -= math.cos(self.angle) * self.speed

	def accelerate(self, vector):
		#Change angle and speed by a given vector		
		(self.angle, self.speed) = addVectors((self.angle, self.speed), vector)


class Spring:
	#This defines the spring and it;s orgional length and strength
	def __init__(self, p1, p2, length=segWide, strength=1):
		self.p1 = p1
		self.p2 = p2
		self.length = length
		self.origLength = length
		self.strength = strength
	
	#This updates the points that are on either end of this spring
	#Not my code but based on a spring someone else designed
	def update(self):
		dx = self.p1.x - self.p2.x
		dy = self.p1.y - self.p2.y
		dist = math.hypot(dx, dy)
		theta = math.atan2(dy, dx)
		force = (self.length - dist) * self.strength
		
		self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
		self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))

		#The damp amount is based on a Maxwell fluid and the idea is that
		# the more force that is being applied the more that the spring
		# loses
		dampAmount = (force*(1-math.exp(-dampCons)))

		self.length -= dampAmount

	#This slowly gets the spring back to its origional length if it is not
	# being activated
	def restore(self):
		if self.length < self.origLength:
			self.length += 0.5

def setUp():
	#This defines the points for the first two points
	topY = height/2 - segTall/2
	bottomY = height/2 + segTall/2

	#These are the points on the arm that don't move
	anchors = [MassPoint((0,topY),size =5),MassPoint((0,bottomY),size = 5)]

	#arrays for points and springs
	points = []
	springs = []

	for x in range(numSegs):
		#Determines the height of the new segment based on the shrink modifier
		newSegLen = (segTall/2)*(shinkMod**(x+1))

		#Determines the new top and bottom for points
		topY = height/2 - newSegLen
		bottomY = height/2 + newSegLen

		#Creates new top and bottom points
		newUpPoint = MassPoint((segWide*(x+1),topY))
		newDownPoint = MassPoint((segWide*(x+1),bottomY))

		#if it is the first set of points the anchors are the points
		# toa attach to. Otherwise use the last points in the array.
		if x == 0:
			oldUpPoint = anchors[0]
			oldDownPoint = anchors[1]
		else:
			oldUpPoint = points[-2]
			oldDownPoint = points[-1]
		
		#Makes a new spring on top between old and new top points
		upSpring = Spring(oldUpPoint,newUpPoint)
		#Makes new spring between top and bottom new points.
		midSpring = Spring(newUpPoint,newDownPoint,length = bottomY-topY,strength=2)
		#Makes new spring on bottom between old and new bottom points
		downSpring = Spring(oldDownPoint,newDownPoint)
		#Makes a spring going top to bottom between old and new points. Is stronger for support
		top2botSpring = Spring(oldUpPoint,newDownPoint,length = calcDist(oldUpPoint,newDownPoint),strength=2)
		#Makes a spring going bottom to top between old and new points. Is stronger for support
		bot2tobSpring = Spring(oldDownPoint,newUpPoint,length = calcDist(oldDownPoint,newUpPoint),strength=2)

		#Appends all points and spring to their arrays
		points.append(newUpPoint)
		points.append(newDownPoint)
		springs.append(upSpring)
		springs.append(midSpring)
		springs.append(downSpring)
		springs.append(top2botSpring)
		springs.append(bot2tobSpring)

	return [anchors,springs,points]

#Makes it run 
running = True
#Defines how much the segments shrink when active, and the minimum length
moveAmount = -0.5
minLen = segWide/2

#Sets the keys for moving the arm
upKeys = [pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_r,pygame.K_t,pygame.K_y,pygame.K_u,pygame.K_i,pygame.K_o,pygame.K_p]
downKeys = [pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_j,pygame.K_k,pygame.K_l,pygame.K_SEMICOLON]

(anchors,springs,points) = setUp()

targetPoint = makeTarget()
tip = [points[-1],points[-2],points[-3],points[-4]]
score = 0

#Pygame running loop
while running:
	#Gets the keys pressed 
	keys = pygame.key.get_pressed()

	upActive = [random.randint(0,1) for i in range(10)]
	downActive = [random.randint(0,1) for i in range(10)]
	

	#10 is the number of keys, so check all top and bottom keys
	for i in range(10):
		#segNum is to have each key control 2 segments
		segNum = i*2
		#If upKeys i is pressed.....
	 	if keys[upKeys[i]]:
	 		#If the springs are not too small....
	 		if(springs[segNum*5].length > minLen):
	 			#Then shrink them by moveAmount
	 			springs[segNum*5].length += moveAmount
	 		#This moves the next spring over as well
	 		if(springs[(segNum+1)*5].length > minLen):
	 			springs[(segNum+1)*5].length += moveAmount
	 	#Otherwise....
	 	else:
	 		#Start restoring them to their old length
	 		springs[segNum*5].restore()
	 		springs[(segNum+1)*5].restore()

	 	#If downKeys i is pressed.....
	 	if keys[downKeys[i]]:
	 		#If the springs are not too small....
	 		if(springs[segNum*5+2].length > minLen):
	 			#Then shrink them by moveAmount
	 			springs[segNum*5+2].length += moveAmount
	 		#This moves the next spring over as well
	 		if(springs[(segNum+1)*5+2].length > minLen):
	 			springs[(segNum+1)*5+2].length += moveAmount

	 	#Otherwise....
	 	else:
	 		#Start restoring them to their old length
	 		springs[segNum*5+2].restore()
	 		springs[(segNum+1)*5+2].restore()

	#If you close the window it ends
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		 	running = False

	#Makes the screen white
	screen.fill((255,255,255))

	#Updates springs and then draws them
	for s in springs:
		s.update()
		pygame.draw.aaline(screen, (0,0,255), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))

	#Moves points and then draws them
	for p in points:
		p.move()
		pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)

	#Draws anchors
	for a in anchors:
		pygame.draw.circle(screen, a.colour, (int(a.x), int(a.y)), a.size, 0)

	#Shows tip in red
	for t in tip:
		pygame.draw.circle(screen, (255,0,0), (int(t.x), int(t.y)), t.size, 0)

	pygame.draw.circle(screen, (255,0,0), targetPoint, 3, 0)

	if gotTarget(targetPoint,tip):
		score += 1
		targetPoint = makeTarget()
		(anchors,springs,points) = setUp()
		tip = [points[-1],points[-2],points[-3],points[-4]]

	text = font.render(str(score), 1, (255,0,0))
	screen.blit(text,[750,10])

	#Puts all drawing on the screen
	pygame.display.flip()






