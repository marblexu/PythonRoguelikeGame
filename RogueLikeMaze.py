from random import randint, choice
from GameMap import *

class Rect():
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
	
	def isOverLap(self, rect, margin=0):
		if (self.x + self.width + margin> rect.x and 
		    self.y + self.height + margin> rect.y and
			rect.x + rect.width + margin> self.x and 
			rect.y + rect.height + margin> self.y):
			return True
		else:
			return False
	
	def carveRoom(self, map):
		for offset_x in range(self.width):
			for offset_y in range(self.height):
				map.setMap(self.x + offset_x, self.y + offset_y, MAP_ENTRY_TYPE.MAP_EMPTY)
		
#https://github.com/munificent/hauberk/blob/db360d9efa714efb6d937c31953ef849c7394a39/lib/src/content/dungeon.dart
def addRooms(map, room_num, max_size):
	tmp_size = max_size//2
	rooms = []
	for i in range(room_num):
		overlap = False
		size = randint(1, tmp_size) * 2 + 1
		rectangularity = randint(0, size//2) * 2
		width, height = size, size
		if randint(0, 1) == 0:
			width += rectangularity
		else:
			height += rectangularity
		
		x = randint(1, (map.width - width)//2 - 1) * 2 + 1
		y = randint(1, (map.height - height)//2 - 1) * 2 + 1
		
		if x == 0 and y == 0:
			continue

		room = Rect(x, y, width, height)
		
		for entry in rooms:
			if room.isOverLap(entry, 2):
				overlap = True
				break;
		
		if overlap:
			continue
		
		rooms.append(room)
		room.carveRoom(map)
	map.room_list = rooms

def checkAdjacentPos(map, x, y, width, height, checklist):
	directions = []
	if x > 0:
		if not map.isVisited(2*(x-1)+1, 2*y+1):
			directions.append(WALL_DIRECTION.WALL_LEFT)
				
	if y > 0:
		if not map.isVisited(2*x+1, 2*(y-1)+1):
			directions.append(WALL_DIRECTION.WALL_UP)

	if x < width -1:
		if not map.isVisited(2*(x+1)+1, 2*y+1):
			directions.append(WALL_DIRECTION.WALL_RIGHT)
		
	if y < height -1:
		if not map.isVisited(2*x+1, 2*(y+1)+1):
			directions.append(WALL_DIRECTION.WALL_DOWN)
		
	if len(directions):
		direction = choice(directions)
		#print("(%d, %d) => %s" % (x, y, str(direction)))
		if direction == WALL_DIRECTION.WALL_LEFT:
				map.setMap(2*(x-1)+1, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x-1, y))
		elif direction == WALL_DIRECTION.WALL_UP:
				map.setMap(2*x+1, 2*(y-1)+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x+1, 2*y, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x, y-1))
		elif direction == WALL_DIRECTION.WALL_RIGHT:
				map.setMap(2*(x+1)+1, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x+2, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x+1, y))
		elif direction == WALL_DIRECTION.WALL_DOWN:
			map.setMap(2*x+1, 2*(y+1)+1, MAP_ENTRY_TYPE.MAP_EMPTY)
			map.setMap(2*x+1, 2*y+2, MAP_ENTRY_TYPE.MAP_EMPTY)
			checklist.append((x, y+1))
		return True
	else:
		# if not find any unvisited adjacent entry
		return False
		
def growMaze(map, width, height):
	# Use Random Prim algorithm
	# always start in (0,0)
	startX, startY = (0, 0)
	print("start(%d, %d)" % (startX, startY))
	map.setMap(2*startX+1, 2*startY+1, MAP_ENTRY_TYPE.MAP_EMPTY)
	
	checklist = []
	checklist.append((startX, startY))
	while len(checklist):
		# select a random entry from checklist
		entry = choice(checklist)	
		if not checkAdjacentPos(map, entry[0], entry[1], width, height, checklist):
			# the entry has no unvisited adjacent entry, so remove it from checklist
			checklist.remove(entry)


def connectRegions(map, width, height):
	# find the root of the tree which the node belongs to
	def findSet(parent, index):
		if index != parent[index]:
			return findSet(parent, parent[index])
		return parent[index]
	
	def getNodeIndex(x, y):
		return x * height + y
	
	# union two unconnected trees
	def unionSet(parent, index1, index2, weightlist):
		root1 = findSet(parent, index1)
		root2 = findSet(parent, index2)
		if root1 == root2:
			return
		if root1 != root2:
			# take the high weight tree as the root, 
			# make the whole tree balance to achieve everage search time O(logN)
			if weightlist[root1] > weightlist[root2]:
				parent[root2] = root1
				weightlist[root1] += 1
			else:
				parent[root1] = root2
				weightlist[root2] += 1

	def unionAdjacentPos(map, x, y, width, height, parentlist, weightlist, carveWall):
		directions = []
		node1 = getNodeIndex(x,y)
		root1 = findSet(parentlist, node1)
		# check four adjacent entries, add any unconnected entries
		if x > 0:		
			root2 = findSet(parentlist, getNodeIndex(x-1, y))
			if root1 != root2 and (carveWall or map.isVisited(2*x, 2*y+1)):
				directions.append(WALL_DIRECTION.WALL_LEFT)
					
		if y > 0:
			root2 = findSet(parentlist, getNodeIndex(x, y-1))
			if root1 != root2 and (carveWall or map.isVisited(2*x+1, 2*y)):
				directions.append(WALL_DIRECTION.WALL_UP)

		if x < width -1:
			root2 = findSet(parentlist, getNodeIndex(x+1, y))
			if root1 != root2 and (carveWall or map.isVisited(2*x+2, 2*y+1)):
				directions.append(WALL_DIRECTION.WALL_RIGHT)
			
		if y < height -1:
			root2 = findSet(parentlist, getNodeIndex(x, y+1))
			if root1 != root2 and (carveWall or map.isVisited(2*x+1, 2*y+2)):
				directions.append(WALL_DIRECTION.WALL_DOWN)
			
		if len(directions):
			# choose one of the unconnected adjacent entries
			direction = choice(directions)
			if direction == WALL_DIRECTION.WALL_LEFT:
				adj_x, adj_y = (x-1, y)
				map.setMap(2*x, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)				
			elif direction == WALL_DIRECTION.WALL_UP:
				adj_x, adj_y = (x, y-1)
				map.setMap(2*x+1, 2*y, MAP_ENTRY_TYPE.MAP_EMPTY)
			elif direction == WALL_DIRECTION.WALL_RIGHT:
				adj_x, adj_y = (x+1, y)
				map.setMap(2*x+2, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
			elif direction == WALL_DIRECTION.WALL_DOWN:
				adj_x, adj_y = (x, y+1)
				map.setMap(2*x+1, 2*y+2, MAP_ENTRY_TYPE.MAP_EMPTY)
			
			node2 = getNodeIndex(adj_x, adj_y)
			unionSet(parentlist, node1, node2, weightlist)
			return True
		else:
			# the four adjacent entries are all connected, so can remove this entry
			return False
	
	# For Debug: print the generate tree
	def printTree(parent):
		def printPath(parent, x, y):
			node = x * height + y
			path = ''
			while node != parent[node]:
				path = '(' + str(node//height) +','+ str(node%height)+') <= ' + path
				node = parent[node]
			path = '(' + str(node//height) +','+ str(node%height)+') <= ' + path 
			print(path)
		
		for x in range(width):
			for y in range(height):
				printPath(parentlist, x, y)
				
	# Use union find set algorithm
	parentlist = [x*height+y for x in range(width) for y in range(height)]
	#print("parentlist len:", len(parentlist))
	weightlist = [0 for x in range(width) for y in range(height)] 
	checklist = []
	for x in range(width):
		for y in range(height):
			checklist.append((x,y))
		
	while len(checklist):
		# select a random entry from checklist
		entry = choice(checklist)
		if not unionAdjacentPos(map, entry[0], entry[1], width, height, parentlist, weightlist, False):
			checklist.remove(entry)
	#printTree(parentlist)
	#print("=========================================")
	for x in range(width):
		for y in range(height):
			checklist.append((x,y))
		
	while len(checklist):
		# select a random entry from checklist
		entry = choice(checklist)
		if not unionAdjacentPos(map, entry[0], entry[1], width, height, parentlist, weightlist, True):
			checklist.remove(entry)
	#printTree(parentlist)

def getDirections(map, x, y, width, height):
	move_directions = []
	if x > 0:
		if map.isMovable(2*x, 2*y+1):
			move_directions.append((2*x, 2*y+1))
					
	if y > 0:
		if map.isMovable(2*x+1, 2*y):
			move_directions.append((2*x+1, 2*y))

	if x < width -1:
		if map.isMovable(2*x+2, 2*y+1):
			move_directions.append((2*x+2, 2*y+1))
			
	if y < height -1:
		if map.isMovable(2*x+1, 2*y+2):
			move_directions.append((2*x+1, 2*y+2))
		
	return move_directions
	
def isDead(map, x, y, width, height):
	directions = getDirections(map, x, y, width, height)
	if len(directions) <= 1:
		return True
	else:
		return False

def addReduentConnect(map, width, height, factor):
	def addConnect(map, x, y, width, height):
		walls = []
		offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
		for offset in offsets:
			wall_x = 2*x + 1 + offset[0]
			wall_y = 2*y + 1 + offset[1]
			if wall_x >= 1 and wall_x <=  2*width-1 and wall_y >= 1 and wall_y <= 2 * height - 1:
				if not map.isMovable(wall_x, wall_y):
					walls.append((wall_x, wall_y))
		
		wall = choice(walls)
		map.setMap(wall[0], wall[1], MAP_ENTRY_TYPE.MAP_EMPTY)
		print("(%d, %d) set wall empty" % (wall[0], wall[1]))
	
	num = 0
	for x in range(width):
		for y in range(height):
			if isDead(map, x, y, width, height):
				# set one of wall of dead entry to empty by factor
				num += 1
				if num == factor:
					print("(%d, %d) find dead" % (2*x+1, 2*y+1))
					addConnect(map, x, y, width, height)
					num = 0

					
def removeDeadEnds(map, width, height):
	def removeDead(map, x, y, width, height):
		map.setMap(2*x+1, 2*y+1, MAP_ENTRY_TYPE.MAP_BLOCK)
		if x > 0:
			map.setMap(2*x, 2*y+1, MAP_ENTRY_TYPE.MAP_BLOCK)
						
		if y > 0:
			map.setMap(2*x+1, 2*y, MAP_ENTRY_TYPE.MAP_BLOCK)

		if x < width -1:
			map.setMap(2*x+2, 2*y+1, MAP_ENTRY_TYPE.MAP_BLOCK)
				
		if y < height -1:
			map.setMap(2*x+1, 2*y+2, MAP_ENTRY_TYPE.MAP_BLOCK)
			
	while True:
		found = False
		for x in range(width):
			for y in range(height):
				if not map.isMovable(2*x+1, 2*y+1):
					continue
				if isDead(map, x, y, width, height):
					removeDead(map, x, y, width, height)
					print("(%d, %d) set block", 2*x+1, 2*y+1)
					found = True
		if not found:
			break
WIDTH = 25
HEIGHT = 21
ROOM_NUM = WIDTH//2

def generateMaze(map):
	map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)
	room_max_size = map.width//10 if map.width < map.height else map.height//10
	addRooms(map, ROOM_NUM, room_max_size)
	map.showMap()
	growMaze(map, (map.width-1)//2, (map.height-1)//2)
	map.showMap()
	connectRegions(map, (map.width-1)//2, (map.height-1)//2)
	removeDeadEnds(map, (map.width-1)//2, (map.height-1)//2)
	
def run():
	map = Map(WIDTH, HEIGHT)
	generateMaze(map)
	map.showMap()	
	

if __name__ == "__main__":
	run()	