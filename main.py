# pymaze - Maze Generator and Game in Python
# Ole Herman S. Elgesem
# DISCLAIMER: Unoptimized and uncommented - Proceed at your own risk.

# Setup
import pygame, sys
sys.setrecursionlimit(10000) 
from pygame.locals import *
pygame.init()
fpsClock = pygame.time.Clock()

mazeWidth = 22
mazeHeight = 20
pixelUnit = 30
u = pixelUnit
windowWidth = mazeWidth * pixelUnit
windowHeight = mazeHeight * pixelUnit

maze = {}

# 27 primes:
primes = [37,73,43,47,2,83,7,89,41,17,67,71,101,97,3,19,61,5,11,23,53,59,29,13,79,31,103]
# 15 pseudo random numbers:
numbers = [3755,8187,7883,9111,2503,5838,9544,1001,2246,1840,1160,1069,9369,9540,3213]
level = 1
seed = 0
score = 0
checks = [0,0,0]
checksc = [(1, mazeHeight-2),(mazeWidth-2, 1),(mazeWidth-2, mazeHeight-2)]

# Window management
windowSurfaceObj = pygame.display.set_mode((windowWidth,windowHeight))
pygame.display.set_caption('PyMaze - Level:'+str(level)+' Score:'+str(score))

# Global variables for visuals and "game logic"
whiteColor = pygame.Color(255,255,255)
blackColor = pygame.Color(0,0,0)
redColor = pygame.Color(255,0,0)
greenColor = pygame.Color(0,255,0)
playerx, playery = 1,1

def drawSquare(x,y,c):
	pygame.draw.rect(windowSurfaceObj, c, (x*u, y*u, u, u))

def drawMaze():
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			if maze[x,y] == 1:
				drawSquare(x,y,blackColor)

# Fill BG with black and draw player on top
def drawScene():
	pygame.display.set_caption('PyMaze - Level:'+str(level)+' Score:'+str(score))
	windowSurfaceObj.fill(whiteColor)
	drawSquare(playerx,playery,redColor)
	drawMaze()
	for i in range(0,3):
		if checks[i] == 0:
			drawSquare(*checksc[i], c=greenColor)
	
	
	

def isOutside(x,y):
	if x<0 or y<0 or x>=mazeWidth or y>=mazeHeight:
		return True
	return False
	
def isBorder(x,y):
	if x == 0 and (y>=0 and y < mazeHeight):
		return True
	if x == (mazeWidth-1) and (y>=0 and y < mazeHeight):
		return True
	if y == 0 and (x>=0 and x < mazeWidth):
		return True
	if y == mazeHeight-1 and (x>=0 and x < mazeWidth):
		return True
	return False

def isBlocked(x,y):
	if( x<0 or y<0 or x>=mazeWidth or y>= mazeHeight ):
		return True
	if(maze[x,y] == 1):
		return True
	return False

def countBlockedX(x,y):
	count = 0
	if isBlocked(x-1,y-1):
		count += 1
	if isBlocked(x+1,y-1):
		count += 1
	if isBlocked(x-1, y+1):
		count += 1
	if isBlocked(x+1, y+1):
		count += 1
	return count
	
def countBlockedPlus(x,y):
	count = 0
	if isBlocked(x,y-1):
		count += 1
	if isBlocked(x, y+1):
		count += 1
	if isBlocked(x-1, y):
		count += 1
	if isBlocked(x+1, y):
		count += 1
	return count

def countBlockedNeighbors(x,y):
	return countBlockedPlus(x,y) + countBlockedX(x,y)

# Moves player by (x*unit, y*unit)
def playerMove(x,y):
	global playerx
	global playery
	playerx += x
	playery += y
	if(isBlocked(playerx,playery)):
		playerx -= x
		playery -= y
	num = countOpenNeighbors(x,y)

def countOpenNeighbors(x,y):
	return (8 - countBlockedNeighbors(x,y))

def countOpenPlus(x,y):
	return (4 - countBlockedPlus(x,y))

def countEscapes(x,y):
	count = 0
	if(countOpenPlus(x,y-1) >= 2):
		count += 1
	if(countOpenPlus(x,y+1) >= 2):
		count += 1
	if(countOpenPlus(x-1,y) >= 2):
		count += 1
	if(countOpenPlus(x+1,y) >= 2):
		count += 1
	
	return count

def recursiveSearch(x,y):
	if isBlocked(x,y):
		return
	if maze[x,y] == 10:
		return
	if not isBlocked(x,y):
		maze[x,y] = 10
		recursiveSearch(x-1,y)
		recursiveSearch(x+1,y)
		recursiveSearch(x,y-1)
		recursiveSearch(x,y+1)
		
def recursiveSearchStart(x,y):
	recursiveSearch(x,y)
	rval = True						# True means everything went ok
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			if( maze[x,y] == 0 ):
				rval = False		# Means we can't place here
			if( maze[x,y] == 10 ):
				maze[x,y] = 0
	return rval

def tryPlace(x,y):
	if(isBlocked(x,y)):
		return False
	maze[x,y] = 1
	if recursiveSearchStart(1,1):
		drawScene()
		pygame.display.update()
		return True
	maze[x,y] = 0
	return False

def cellGen(x,y):
	if isBlocked(x-1,y) and isBlocked(x-1,y-1) and isBlocked(x,y-1):
		return
	if isBlocked(x+1,y) and isBlocked(x+1,y-1) and isBlocked(x,y-1):
		return
	if isBlocked(x-1,y) and isBlocked(x-1,y+1) and isBlocked(x,y+1):
		return
	if isBlocked(x+1,y) and isBlocked(x+1,y+1) and isBlocked(x,y+1):
		return
	tryPlace(x,y)
	return

def generate():
	global checks
	global playerx
	global playery
	playerx = 1
	playery = 1
	checks = [0,0,0]
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			maze[x,y] = 0
			if isBorder(x,y):
				maze[x,y] = 1
	i = 0
	x = 0
	y = 0
	global seed
	seed = level + 111 + level/3 + level/5
	n = seed%15
	rand = {}
	for i in range(0,256):
		if(n>14):
			n=0
		rand[i] = seed * numbers[n] + i
		for p in range(0, 27):
			rand[i] += i/primes[p]
	i = 0
	while i<255:
		num = rand[i]
		x = num%mazeWidth
		i += 1
		num = rand[i]
		y = num%mazeHeight
		i += 1
		cellGen(x,y);
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			cellGen(x,y)
			x2 = mazeWidth-1-x
			y2 = mazeHeight-1-y
			cellGen(x2, y2)
			cellGen(x2/2, y2/2)
			if(x > 5 and y%x == 0):
				for x3 in range(x, x+mazeWidth/2):
					cellGen(x3, y)
	global mUp
	mUp = False
	global mLeft
	mLeft = False
	global mDown
	mDown = False
	global mRight
	mRight = False
			
	
		
# Moves player by (x*unit, y*unit)
def playerMove(x,y):
	global playerx
	global playery
	global score
	global level
	global checks
	global checksc
	playerx += x
	playery += y
	if(isBlocked(playerx,playery)):
		playerx -= x
		playery -= y
		return
	c = (playerx,playery)
	for i in range(0,3):
		if(checksc[i] == c):
			checks[i] = 1
			score += 1
			if(checks[0] == 1 and checks[1] == 1 and checks[2] == 1):
				level += 1
				generate()
				return
			
			
def movement():
	if mUp:
		playerMove(0,-1)
	if mLeft:
		playerMove(-1,0)
	if mDown:
		playerMove(0,1)
	if mRight:
		playerMove(1,0)
	

mUp = False
mLeft = False
mDown = False
mRight = False
generate()
# Infinite loop can be broken by quit event
while True:
	#Handle events:
	events = 0
	for event in pygame.event.get():
		events += 1
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == KEYDOWN:
			if event.key == K_w:
				mUp = True
				movement()
			if event.key == K_a:
				mLeft = True
				movement()
			if event.key == K_s:
				mDown = True
				movement()
			if event.key == K_d:
				mRight = True
				movement()
			if event.key == K_SPACE:
				generate()
			if event.key == K_ESCAPE:
				pygame.event.post(pygame.event.Event(QUIT))
		elif event.type == KEYUP:
			if event.key == K_w:
				mUp = False
			if event.key == K_a:
				mLeft = False
			if event.key == K_s:
				mDown = False
			if event.key == K_d:
				mRight = False
	#Drawing scene and updating window:
	if(events == 0):
		movement()
	drawScene()
	pygame.display.update()
	fpsClock.tick(10)
