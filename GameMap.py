from random import randint
from enum import IntEnum
import pygame
from pygame.locals import *

REC_SIZE = 50
WALL_SIZE = 20
ENTITY_SIZE = 15
REC_X_NUM = 69 # must be odd number
REC_Y_NUM = 41 # must be odd number
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 120
MAP_WIDTH = REC_X_NUM//2 * REC_SIZE + REC_X_NUM//2 * WALL_SIZE + WALL_SIZE
MAP_HEIGHT = REC_Y_NUM//2 * REC_SIZE + REC_Y_NUM//2 * WALL_SIZE + WALL_SIZE
MAP_REDUCE_RATIO = 10
MAPS_INTERVAL = 20
SMALL_MAP_WIDTH = MAP_WIDTH//MAP_REDUCE_RATIO
SCREEN_WIDTH = min(900, MAP_WIDTH)
SCREEN_HEIGHT = min(500, MAP_HEIGHT) + BUTTON_HEIGHT

class MAP_ENTRY_TYPE(IntEnum):
	MAP_EMPTY = 0,
	MAP_BLOCK = 1,
	MAP_TARGET = 2,
	MAP_PATH = 3,

class WALL_DIRECTION(IntEnum):
	WALL_LEFT = 0,
	WALL_UP = 1,
	WALL_RIGHT = 2,
	WALL_DOWN = 3,

class MOVE_DIRECTION(IntEnum):
	MOVE_LEFT = 0,
	MOVE_UP = 1,
	MOVE_RIGHT = 2,
	MOVE_DOWN = 3,
	
map_entry_types = {0:MAP_ENTRY_TYPE.MAP_EMPTY, 1:MAP_ENTRY_TYPE.MAP_BLOCK, 2:MAP_ENTRY_TYPE.MAP_TARGET, 3:MAP_ENTRY_TYPE.MAP_PATH}
map_wall_direction = {0:WALL_DIRECTION.WALL_LEFT, 1:WALL_DIRECTION.WALL_UP, 2:WALL_DIRECTION.WALL_RIGHT, 3:WALL_DIRECTION.WALL_DOWN}

class Map():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.screen_width = (REC_SIZE + WALL_SIZE) * (width // 2) + WALL_SIZE
		self.screen_height = (REC_SIZE + WALL_SIZE) * (height // 2) + WALL_SIZE
		self.map = [[0 for x in range(self.width)] for y in range(self.height)]
		self.frog_map = [[0 for x in range(self.width)] for y in range(self.height)]
		self.walls = [[(1, 1, 1, 1) for x in range(self.width)] for y in range(self.height)]
		self.room_list = None
		self.hero = None
		
	def createBlock(self, block_num):
		for i in range(block_num):
			x, y = (randint(0, self.width-1), randint(0, self.height-1))
			self.map[y][x] = 1
	
	def generatePos(self, rangeX, rangeY, type=MAP_ENTRY_TYPE.MAP_EMPTY):
		if type == MAP_ENTRY_TYPE.MAP_EMPTY:
			value = 0
		else:
			value = 1
		x, y = (randint(rangeX[0], rangeX[1]), randint(rangeY[0], rangeY[1]))
		while self.map[y][x] != value:
			x, y = (randint(rangeX[0], rangeX[1]), randint(rangeY[0], rangeY[1]))
		return (x , y)

	def generateEntityPos(self, rangeX, rangeY):
		x, y = (randint(rangeX[0], rangeX[1]), randint(rangeY[0], rangeY[1]))
		while x % 2 == 0 or y % 2 ==0 or self.map[y][x] == 1:
			x, y = (randint(rangeX[0], rangeX[1]), randint(rangeY[0], rangeY[1]))
		return (x , y)
		
	def resetMap(self, value):
		for y in range(self.height):
			for x in range(self.width):
				self.setMap(x, y, value)
	
	def resetFrog(self, value):
		for y in range(self.height):
			for x in range(self.width):
				self.frog_map[y][x] = value
	
	def clearFrog(self, x, y, distance):
		for i in range(x - distance, x + distance + 1):
			for j in range(y - distance, y + distance + 1):
				if self.isValid(i,j):
					self.frog_map[j][i] = 0
	
	def isFrog(self, x, y):
		return self.frog_map[y][x] == 1
	
	def setMap(self, x, y, value):
		if value == MAP_ENTRY_TYPE.MAP_EMPTY:
			self.map[y][x] = 0
		elif value == MAP_ENTRY_TYPE.MAP_BLOCK:
			self.map[y][x] = 1
		elif value == MAP_ENTRY_TYPE.MAP_TARGET:
			self.map[y][x] = 2
		else:
			self.map[y][x] = 3
	
	def isVisited(self, x, y):
		return self.map[y][x] != 1

	def isMovable(self, x, y):
		return self.map[y][x] != 1
	
	def isValid(self, x, y):
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return False
		return True
	
	def getType(self, x, y):
		return map_entry_types[self.map[y][x]]
	
	def showMap(self):
		print("+" * (2*self.width + 2))

		for row in self.map:
			s = '+'
			for entry in row:
				if entry == 0:
					s += ' 0'
				elif entry == 1:
					s += ' #'
				else:
					s += ' X'
			s += '+'
			print(s)

		print("+" * (2*self.width + 2))
	
	# below functions added for show in pygame sceen
	def indexToMapPos(self, x, y):
		map_x = x//2 * REC_SIZE + x//2 * WALL_SIZE
		map_y = y//2 * REC_SIZE + y//2 * WALL_SIZE

		if x % 2 == 1 and y % 2 == 1:
			map_x += WALL_SIZE
			map_y += WALL_SIZE
		elif x % 2 == 0 and  y % 2 == 1:
			map_y += WALL_SIZE
		elif x % 2 == 1 and y % 2 == 0:
			map_x += WALL_SIZE
		
		return (map_x, map_y)	
	
	def MapPosToIndex(self, map_x, map_y):
		num_x = map_x // (REC_SIZE + WALL_SIZE)
		num_y =  map_y // (REC_SIZE + WALL_SIZE)
		map_x -= num_x * (REC_SIZE + WALL_SIZE)
		map_y -= num_y * (REC_SIZE + WALL_SIZE)
		if map_x < WALL_SIZE :
			x = num_x * 2
		elif map_x >= WALL_SIZE and map_x <= WALL_SIZE + REC_SIZE:
			x = num_x * 2 + 1
		
		if map_y < WALL_SIZE :
			y = num_y * 2
		elif map_y >= WALL_SIZE and map_y <= WALL_SIZE + REC_SIZE:
			y = num_y * 2 + 1
		return (x, y)
	
	def isInMap(self, map_x, map_y, entity_width, entity_height):
		if (map_x >= WALL_SIZE and map_y >= WALL_SIZE and
			map_x <= (self.screen_width - WALL_SIZE - entity_width) and map_y <= (self.screen_height - WALL_SIZE - entity_height)):
			return True
		return False
	
	def isMovableInMap(self, map_x, map_y, entity_width, entity_height):
		offsets = [(0, 0), (0, entity_height), (entity_width, 0), (entity_width, entity_height)]
		for offset in offsets:
			x, y = self.MapPosToIndex(map_x + offset[0], map_y + offset[1])
			if not self.isMovable(x, y):
				return False
	
		return True
	
	def getMapUnitRect(self, x, y):
		map_x = x//2 * REC_SIZE + x//2 * WALL_SIZE
		map_y = y//2 * REC_SIZE + y//2 * WALL_SIZE

		if x % 2 == 0 and y % 2 == 0:
			width, height = (WALL_SIZE, WALL_SIZE)
		elif x % 2 == 1 and y % 2 == 1:
			width, height = (REC_SIZE, REC_SIZE)
			map_x += WALL_SIZE
			map_y += WALL_SIZE
		elif x % 2 == 0 and  y % 2 == 1:
			width, height = (WALL_SIZE, REC_SIZE)
			map_y += WALL_SIZE
		else:
			width, height = (REC_SIZE, WALL_SIZE)
			map_x += WALL_SIZE
		
		return (map_x, map_y, width, height)
		
class ScreenShow():
	def __init__(self, width, height, start_x, start_y, map):
		self.width = width
		self.height = height
		self.map = map
		self.offset_x = 0
		self.offset_y = 0
		self.start_x = start_x
		self.start_y = start_y 
	
	def screenToMapPos(self, screen_x, screen_y):
		return (screen_x + self.offset_x, screen_y + self.offset_y)
	
	def screenToMapIndex(self, screen_x, screen_y):
		map_x, map_y = self.screenToMapPos(screen_x, screen_y)
		return self.map.MapPosToIndex(map_x, map_y)

	def mapToScreenPos(self, map_x, map_y):		
		return (map_x - self.offset_x, map_y - self.offset_y)
	
	def getDrawLoaction(self, screen_x, screen_y):
		return (screen_x + self.start_x, screen_y + self.start_y)
	
	# update screen offset after hero move
	def updateOffset(self, hero, action):
		map_x, map_y = self.screenToMapPos(hero.screen_x, hero.screen_y)
		#print("map(%d, %d), screen(%d, %d) width(%d) screen_width(%d)" % (map_x, map_y, hero.screen_x, hero.screen_y, self.width, self.map.screen_width))
		if map_x > self.width//2 and map_x < self.map.screen_width - self.width//2:
			self.offset_x += action[0]
			hero.screen_x -= action[0]
		if map_y > self.height//2 and map_y < self.map.screen_height - self.height//2:
			self.offset_y += action[1]
			hero.screen_y -= action[1]
		
	def checkMovable(self, screen_x, screen_y, entity_width, entity_height):
		map_x, map_y = self.screenToMapPos(screen_x, screen_y)
		if (self.map.isInMap(map_x, map_y, entity_width, entity_height) and
			self.map.isMovableInMap(map_x, map_y, entity_width, entity_height)):
			return True
		return False
	
	def mapIndexToScreen(self, x, y):
		map_x, map_y = self.map.indexToMapPos(x, y)
		return self.mapToScreenPos(map_x, map_y)		
	
	def getSmallMapRect(self, map_x, map_y, width, height, reduce_ratio):
		small_map_x = map_x // reduce_ratio
		small_map_y = map_y // reduce_ratio
		small_location_x = small_map_x + self.width + MAPS_INTERVAL
		small_location_y = small_map_y + BUTTON_HEIGHT
		small_width = width // reduce_ratio
		small_height = height // reduce_ratio
		return (small_location_x, small_location_y, small_width, small_height)		
	
	def screenToSmallMapRect(self, screen_x, screen_y, width, height):
		map_x, map_y = self.screenToMapPos(screen_x, screen_y)
		return self.getSmallMapRect(map_x, map_y, width, height, MAP_REDUCE_RATIO)
		
	def drawBackground(self, screen):		
		for y in range(self.map.height):
			for x in range(self.map.width):
				if self.map.isFrog(x,y):
					color = (128, 128, 128)
				else:
					type = self.map.getType(x, y)
					
					if type == MAP_ENTRY_TYPE.MAP_EMPTY:
						color = (255, 255, 255)
					elif type == MAP_ENTRY_TYPE.MAP_BLOCK:
						color = (0, 0, 0)
					elif type == MAP_ENTRY_TYPE.MAP_TARGET:
						color = (255, 0, 0)
					else:
						color = (0, 255, 0)
				
				map_x, map_y, width, height = self.map.getMapUnitRect(x, y)
				screen_x, screen_y = self.mapToScreenPos(map_x, map_y)
												
				# draw small map
				small_location_x, small_location_y, small_width, small_height = self.getSmallMapRect(map_x, map_y, width, height, MAP_REDUCE_RATIO)
				pygame.draw.rect(screen, color, pygame.Rect(small_location_x, small_location_y, small_width, small_height))
				
				# draw map
				if (screen_x >= 0 and screen_x < self.width and 
					screen_y >= 0 and screen_y < self.height):
					location_x, location_y = self.getDrawLoaction(screen_x, screen_y)
					if screen_x + width > self.width:
						width = self.width - screen_x
					if screen_y + height > self.height:
						height = self.height - screen_y
					pygame.draw.rect(screen, color, pygame.Rect(location_x, location_y, width, height))

				
				
				
				
				

