'''============================================================================

File: main.py
From project: pyMaze - Maze generator and game in Python
Date: 2015-03-29
Author: olehermanse ( http://www.github.com/olehermanse )
License: The MIT License (MIT)

The MIT License (MIT)

Copyright (c) 2015 olehermanse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

============================================================================'''

# DISCLAIMER: Unoptimized and uncommented - Proceed at your own risk.

# =================INIT====================
import pygame, sys, os.path
sys.setrecursionlimit(10000) 
from pygame.locals import *
pygame.init()
fpsClock = pygame.time.Clock()

# =================VARIABLES====================
# Constants
mazeWidth = 22
mazeHeight = 18
u = pixelUnit = 30
windowWidth = mazeWidth * pixelUnit
windowHeight = mazeHeight * pixelUnit

# Maze is a 2D array of integers
maze = {}

# Maze variables - used for generation
primes = [37,73,43,47,2,83,7,89,41,17,67,71,101,97,3,19,61,5,11,23,53,59,29,13,79,31,103]
numbers = [3755,8187,7883,9111,2503,5838,9544,1001,2246,1840,1160,1069,9369,9540,3213]
level = 1
seed = 0
seedPlus = 0

# Corner variables - gameplay
checks = [0,0,0]
checksc = [(1, mazeHeight-2),(mazeWidth-2, 1),(mazeWidth-2, mazeHeight-2)]

# Player variables
score = 0
scorePerLevel = 0
playerx, playery = 1,1
minutes = 0
seconds = 0
secondsLevel = 0
secondsTotal = 0
secondsAverage = 0
frames = 0
fps = 14
highScore = 0
oldScore = 0
playerName = 'P1'

# Pygame window
windowSurfaceObj = pygame.display.set_mode((windowWidth,windowHeight))
updateRect = pygame.Rect(0,0,u,u)

# Color variables
whiteColor = pygame.Color(255,255,255)
blackColor = pygame.Color(0,0,0)
redColor = pygame.Color(255,0,0)
greenColor = pygame.Color(0,255,0)

def minit():
	global level, seed, seedPlus
	level = 1
	seed = seedPlus = 0
	global score, scorePerLevel, highScore, oldScore
	score = scorePerLevel = highScore = oldScore = 0
	global minutes, seconds, secondsLevel, secondsTotal, secondsAverage
	minutes = seconds = secondsLevel = secondsTotal = secondsAverage = 0
	global frames
	frames = 0

# Draw a square with color c at (x,y) in our grid of squares with u width
def drawSquare(x,y,c):
	global u
	pygame.draw.rect(windowSurfaceObj, c, (x*u, y*u, u, u))

# Draw maze walls without player or objectives
def drawMaze():
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			if maze[x,y] == 1:
				drawSquare(x,y,blackColor)

def updateText():
	global score, level, scorePerLevel, playerName
	global minutes, seconds, frames, secondsLevel, secondsAverage
	levelmsg = ' Level:'+ str(level)+'('+str(seedPlus)+')'
	scoremsg = ' Score:'+str(score)+'~'+str(scorePerLevel)+'per level'
	timemsg = ' - Time:'+str(minutes)+'m'+str(seconds)+'s'
	if( frames < 10 ):
		timemsg = timemsg+'0'
	timemsg = timemsg+str(frames)+'f Current:'+str(secondsLevel)
	timemsg = timemsg+'s Average: '+str(secondsAverage)+'s'
	msg = 'PyMaze - '+playerName+' - '+levelmsg+scoremsg+timemsg
	pygame.display.set_caption(msg)

# Draw maze, objectives and player. Update score display
def drawScene():
	global minutes, seconds, frames, secondsLevel, secondsTotal
	frames += 1
	if(frames >= fps):
		seconds += 1
		secondsLevel += 1
		secondsTotal += 1
		frames = 0
	if(seconds >= 60):
		minutes += 1
		seconds = 0
	updateText()
	windowSurfaceObj.fill(whiteColor)
	drawSquare(playerx,playery,redColor)
	drawMaze()
	for i in range(0,3):
		if checks[i] == 0:
			drawSquare(*checksc[i], c=greenColor)
	pygame.display.update()
			
# Check if game world coordinate is outside of maze
def isOutside(x,y):
	if x<0 or y<0 or x>=mazeWidth or y>=mazeHeight:
		return True
	return False

# Check if game world coordinate is on the edge of the maze	
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

# Check if a game world coordinate is blocked by wall
def isBlocked(x,y):
	if( x<0 or y<0 or x>=mazeWidth or y>= mazeHeight ):
		return True
	if(maze[x,y] == 1):
		return True
	return False

# Recursive function - Visits all accessible parts of maze
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

# Starts a recursive search to see if all of the maze is accessible
def recursiveSearchStart(x,y):
	recursiveSearch(x,y)
	rval = True						# rval == true means the search visited everything
	for x in range(1, mazeWidth-1):			# ignore first and last row and column
		for y in range(1, mazeHeight-1):	# they are always walls
			if( maze[x,y] == 0 ):
				rval = False		# We found something the search didn't visit
			if( maze[x,y] == 10 ):
				maze[x,y] = 0
	return rval

# Places a wall, tests if the maze is still valid, reverts change if test fails
def tryPlace(x,y):
	if(isBlocked(x,y)):
		return False
	maze[x,y] = 1
	if recursiveSearchStart(1,1):
		return True
	maze[x,y] = 0
	return False

# Tests whether we want to generate a wall at (x,y) based on 2 factors
def cellGen(x,y):
	# Don't create 2x2 squares:
	if isBlocked(x-1,y) and isBlocked(x-1,y-1) and isBlocked(x,y-1):
		return
	if isBlocked(x+1,y) and isBlocked(x+1,y-1) and isBlocked(x,y-1):
		return
	if isBlocked(x-1,y) and isBlocked(x-1,y+1) and isBlocked(x,y+1):
		return
	if isBlocked(x+1,y) and isBlocked(x+1,y+1) and isBlocked(x,y+1):
		return
	# Don't cut off parts of the maze - tryPlace ensures this
	drawCheck = tryPlace(x,y)
	if drawCheck:
		drawSquare(x,y,blackColor)
		pygame.display.update()
	return

# resets player position and the level
def resetPlayer():
	global checks, playerx, playery, secondsLevel
	playerx = playery = 1
	secondsLevel = 0
	checks = [0,0,0]
	
	global kUp, kLeft, kDown, kRight
	global kW, kA, kS, kD
	kUp = kLeft = kDown = kRight = False
	kW = kA = kS = kD = False

# Generate a maze based on seed and level
def generate():
	resetPlayer()
	for x in range(0, mazeWidth):
		for y in range(0, mazeHeight):
			maze[x,y] = 0
			if isBorder(x,y):
				maze[x,y] = 1
	drawScene()
	i = x = y = 0
	global seed, level, seedPlus
	seed = 111 + 3*(level-1) + level/3 + level/5 + seedPlus
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
	for x in range(1, mazeWidth-1):
		for y in range(1, mazeHeight-1):
			cellGen(x,y)
			x2 = mazeWidth-1-x
			y2 = mazeHeight-1-y
			cellGen(x2, y2)
			cellGen(x2/2, y2/2)
			space = 2+level%4
			if(x > 3 and (x+(4*y/3))%space == 0):
				for y3 in range(y, y+mazeHeight/3):
					cellGen(x, y3)


def nextLevel():
	global level, score, scorePerLevel, seedPlus, oldScore, highScore
	global minutes, seconds, secondsLevel, secondsTotal, secondsAverage
	score += 1
	if(secondsLevel < 200):
		score += (200-secondsLevel)/10
		
	secondsAverage = secondsTotal/level
	if(secondsAverage < 20):
		score += 20 - secondsAverage
	if(secondsLevel < 20):
		score += 20 - secondsLevel
	scorePerLevel = score/level
	if(level == 10 and (score-oldScore) > highScore):
		highScore = score-oldScore
	oldScore = score
	level += 1
	seedPlus = 0
	if(playerx > 1):
		seedPlus += 1
	if(playery > 1):
		seedPlus += 2
	seedPlus -= 1
	writeFile()
	generate()


# Moves player by (x*unit, y*unit)
# All game logic is done through this function
# since nothing happens when standing still
def playerMove(x,y):
	global playerx, playery, score
	global level, secondsLevel, minutes, seconds
	global checks, checksc
	playerx += x
	playery += y
	if(isBlocked(playerx,playery)):
		playerx -= x
		playery -= y
		return
	c = (playerx,playery)
	for i in range(0,3):
		if(checksc[i] == c and checks[i] == 0):
			checks[i] = 1
			if(checks[0] == 1 and checks[1] == 1 and checks[2] == 1):
				nextLevel()
				return
			
# Move player based on keyboard input
def movement():
	if kW or kUp:
		playerMove(0,-1)
	if kA or kLeft:
		playerMove(-1,0)
	if kS or kDown:
		playerMove(0,1)
	if kD or kRight:
		playerMove(1,0)

def exitPyMaze():
	pygame.quit()
	sys.exit()

def readFile():
	if os.path.isfile('save.txt'):
		f = open('save.txt', 'r')
		global level, score, scorePerLevel, seedPlus, playerName
		global minutes, seconds, frames, secondsTotal, secondsAverage
		level, score, minutes, seconds, frames , seedPlus = map(int, f.readline().split())
		playerName = f.readline()[:-1]
		f.close()
		if(level <= 1 or seedPlus >= 3):
			print('PyMaze Error: Corrupt Save')
			exitPyMaze()
		secondsTotal = minutes*60 + seconds
		scorePerLevel = score/(level-1)
		secondsAverage = secondsTotal/(level-1)
		if(scorePerLevel > 150 or secondsAverage < 3):
			print('PyMaze Error: Corrupt Save')
			exitPyMaze()

def writeFile():
	f = open('save.txt', 'w')
	temp = str(level)+' '+str(score)
	temp = temp+' '+str(minutes)+' '+str(seconds)+' '+str(frames)
	temp = temp+' '+str(seedPlus)+'\n'
	temp = temp+playerName+'\n'
	f.write(temp)
	f.close()
	
	
def pad(s, n):
	while(len(s) < n):
		s = s + ' '
	return s

def saveHighScore():
	global score, highScore, level, scorePerLevel, minutes, seconds, frames, playerName
	f = open('highscores.txt', 'a')
	labelS = 'lvl.' + str(level) + ' ' + playerName + ': '
	highS = ' Best = ' + str(highScore)
	totalS = ' Total = '+str(score)
	splS = ' SPL = ' + str(scorePerLevel)
	timeS = ' Time = '+str(minutes)+'m '+str(seconds)+'s '+str(frames)+'f'
	labelS = pad(labelS, 26)
	highS = pad(highS, 14)
	totalS = pad(totalS, 16)
	splS = pad(splS, 12)
	temp = labelS + highS + totalS + splS + timeS + '\n'
	f.write(temp)
	f.close()
	saveHSData()
	
def saveHSData():
	global score, highScore, level, scorePerLevel, minutes, seconds, frames, playerName
	f = open('hsdata.txt', 'a')
	
	temp = str(level)+' '+str(highScore)+' '+str(score)+' '+str(scorePerLevel)+' '
	temp = temp + str(minutes)+' '+str(seconds)+' '+str(frames)+' '+playerName+'\n'
	f.write(temp)
	f.close()

def setName():
	global playerName
	doneTyping = False
	tempName = ''
	while(doneTyping == False):
		events = 0
		for event in pygame.event.get():
			events += 1
			if event.type == QUIT:
				exitPyMaze()
			elif event.type == KEYDOWN:
				if event.key == K_RETURN:
					doneTyping = True
				elif event.key == K_ESCAPE:
					pygame.event.post(pygame.event.Event(QUIT))
				else:
					tempName = tempName + event.unicode
		
		msg = 'Enter name: ' + tempName
		pygame.display.set_caption(msg)
		fpsClock.tick(fps)
	
	playerName = tempName
	

def restart():
	minit()
	if os.path.isfile('save.txt'):
		os.remove('save.txt')
	generate()
	setName()

# Main:
minit()
readFile()
generate()
if(level == 1):
	setName()
while True:
	#Handle events:
	events = 0
	for event in pygame.event.get():
		events += 1
		if event.type == QUIT:
			exitPyMaze()
		# Movement is done once per key down event
		# As well as once per frame if key is held down.
		elif event.type == KEYDOWN:
			if event.key == K_w:
				kW = True
				movement()
			if event.key == K_a:
				kA = True
				movement()
			if event.key == K_s:
				kS = True
				movement()
			if event.key == K_d:
				kD = True
				movement()
			if event.key == K_r:
				saveHighScore()
				restart()
			if event.key == K_UP:
				kUp = True
				movement()
			if event.key == K_LEFT:
				kLeft = True
				movement()
			if event.key == K_DOWN:
				kDown = True
				movement()
			if event.key == K_RIGHT:
				kRight = True
				movement()
			if event.key == K_SPACE:
				readFile()
				generate()
			if event.key == K_ESCAPE:
				pygame.event.post(pygame.event.Event(QUIT))
		elif event.type == KEYUP:
			if event.key == K_w:
				kW = False
			if event.key == K_a:
				kA = False
			if event.key == K_s:
				kS = False
			if event.key == K_d:
				kD = False
			if event.key == K_UP:
				kUp = False
			if event.key == K_LEFT:
				kLeft = False
			if event.key == K_DOWN:
				kDown = False
			if event.key == K_RIGHT:
				kRight = False
	#Drawing scene and updating window:
	if(events == 0):
		movement()		#All game logic is done through movement function
	drawScene()
	fpsClock.tick(fps)
