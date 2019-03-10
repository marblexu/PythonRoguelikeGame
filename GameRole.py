import pygame
from pygame.locals import *
from enum import Enum
from random import randint
from GameMap import *
from AStarSearch import *

class ENEMY_STATE_TYPE(Enum):
	ENEMY_IDLE = 0,
	ENEMY_ATTACK = 1,
	ENEMY_BACK = 2,

class State(object):
	def __init__(self, type):
		self.type = type
	
	def do_actions(self):
		pass
	
	def check_conditions(self):
		pass
	
	def enter_actions(self):
		pass
	
	def exit_actions(self):
		pass


class StateMachine(object):
	def __init__(self):
		self.states = {}
		self.active_state = None
	
	def add_state(self, state):
		self.states[state.type] =  state
	
	def think(self):
		if self.active_state is None:
			return
		self.active_state.do_actions()
		new_state_type = self.active_state.check_conditions()
		if new_state_type is not None:
			self.set_state(new_state_type)
	
	def set_state(self, new_state_type):
		if self.active_state is not None:
			self.active_state.exit_actions()
		self.active_state = self.states[new_state_type]
		self.active_state.enter_actions()

class EnemyEntity(object):
	def __init__(self, enemy_group, name, enemy_surface):
		self.enemy_group = enemy_group
		self.name = name
		self.location = (0, 0) # map position
		self.destination = (0, 0) # map position
		self.speed = 0
		self.brain = StateMachine()
		self.id = 0
		self.time_passed = 0.0
		# init move image
		self.entity_surface = EntitySurface(enemy_surface, 15)
		self.image = self.entity_surface.updateImage()
		self.rect = self.image.get_rect()
		self.width = self.rect.width
		self.height = self.rect.height
		self.moving = False
		self.x = 0 # map index
		self.y = 0 # map index
		
	def render(self, screen, screen_show):
		if not screen_show.map.isFrog(self.x, self.y):
			screen_x, screen_y = screen_show.mapToScreenPos(self.location[0], self.location[1])
			if (screen_x > -self.rect.width and screen_x < screen_show.width and 
				screen_y > -self.rect.height and screen_y < screen_show.height):
				location_x, location_y = screen_show.getDrawLoaction(screen_x, screen_y)
				self.image = self.entity_surface.updateImage()
				screen.blit(self.image, (location_x, location_y, self.rect.width, self.rect.height))
				
				# draw hero in small map
				color = (0, 255, 0)
				small_location_x, small_location_y, small_width, small_height = screen_show.screenToSmallMapRect(screen_x, screen_y, self.rect.width, self.rect.height)
				pygame.draw.rect(screen, color, pygame.Rect(small_location_x, small_location_y, small_width, small_height))
	
	def process(self, time_passed):
		self.brain.think()
		if self.location != self.destination:
			self.time_passed += time_passed
			direction = getMoveDirection(self.location[0], self.location[1], self.destination[0], self.destination[1])
			if self.speed * self.time_passed > 1.0:				
				move_len = int(self.speed * self.time_passed)
				self.time_passed -= move_len/self.speed
				map_x, map_y = self.location
				if direction == MOVE_DIRECTION.MOVE_LEFT:
					map_x -= move_len
					if map_x <= self.destination[0]:
						map_x = self.destination[0]
						self.x -= 1
				elif direction == MOVE_DIRECTION.MOVE_RIGHT:
					map_x += move_len
					if map_x >= self.destination[0]:
						map_x = self.destination[0]
						self.x += 1
				elif direction == MOVE_DIRECTION.MOVE_UP:
					map_y -= move_len
					if map_y <= self.destination[1]:
						map_y = self.destination[1]
						self.y -= 1
				else:
					map_y += move_len
					if map_y >= self.destination[1]:
						map_y = self.destination[1]
						self.y += 1

				self.location = (map_x, map_y)
		else:
			self.moving = False
			self.time_passed = 0

class Enemy(EnemyEntity):
	def __init__(self, enemy_group, enemy_surface, map, room):
		EnemyEntity.__init__(self, enemy_group, "enemy", enemy_surface)
		idle_state = EnemyStateIdle(self, map, room)
		attack_state = EnemyStateAttack(self, map, room)
		back_state = EnemyStateBack(self, map, room)
		self.brain.add_state(idle_state)
		self.brain.add_state(attack_state)
		self.brain.add_state(back_state)
	
	def render(self, surface, screen_show):
		EnemyEntity.render(self, surface, screen_show)			

		
class EnemyStateIdle(State):
	def __init__(self, enemy, map, room):
		State.__init__(self, ENEMY_STATE_TYPE.ENEMY_IDLE)
		self.enemy = enemy
		self.map = map
		self.room = room
		
	def do_actions(self):
		self.enemy.destination = self.enemy.location
	
	def check_conditions(self):
		if self.map.hero is not None:
			if (self.map.hero.x >= self.room.x and self.map.hero.x < self.room.x + self.room.width and
				self.map.hero.y >= self.room.y and self.map.hero.y < self.room.y + self.room.height):
				print("enemy(%d,%d) start to attack" % (self.enemy.location[0], self.enemy.location[1]))
				return ENEMY_STATE_TYPE.ENEMY_ATTACK	
		
		return None
	
	def enter_actions(self):
		self.enemy.speed = 20 + randint(-10, 10)

def getMoveDirection(start_x, start_y, end_x, end_y):
	if start_x < end_x:
		return MOVE_DIRECTION.MOVE_RIGHT
	elif start_x > end_x:
		return MOVE_DIRECTION.MOVE_LEFT
	elif start_y < end_y:
		return MOVE_DIRECTION.MOVE_DOWN
	elif start_y > end_y:
		return MOVE_DIRECTION.MOVE_UP
	else:
		return None

class EnemyStateAttack(State):
	def __init__(self, enemy, map, room):
		State.__init__(self, ENEMY_STATE_TYPE.ENEMY_ATTACK)
		self.enemy = enemy
		self.map = map
		self.room = room
		self.distance = 0
		
	def do_actions(self):
		if self.map.hero is not None:
			if not self.enemy.moving and (self.enemy.x != self.map.hero.x or self.enemy.y != self.map.hero.y):
				location = AStarSearch(self.map, (self.enemy.x, self.enemy.y), (self.map.hero.x, self.map.hero.y))
				if location is not None:
					x, y, distance = getFirstStepAndDistance(location)
					print("enemy(%d,%d) move to (%d,%d) distance %d" % (self.enemy.x, self.enemy.y, x, y, distance))
					self.enemy.destination = self.map.indexToMapPos(x, y)					
					self.distance = distance
					
					self.enemy.moving = True
					direction = getMoveDirection(self.enemy.x, self.enemy.y, x, y)
					if direction is not None:
						self.enemy.entity_surface.updateDirection(direction)
			else:
				x, y = self.map.MapPosToIndex(self.enemy.destination[0], self.enemy.destination[1])
				direction = getMoveDirection(self.enemy.x, self.enemy.y, x, y)
				if direction is not None:
					self.enemy.entity_surface.updateDirection(direction)
	
	def check_conditions(self):
		if self.distance >= 8 and self.enemy.location == self.enemy.destination:
			print("enemy(%d,%d) attack to back" % (self.enemy.x, self.enemy.y))
			return ENEMY_STATE_TYPE.ENEMY_BACK
		return None
	
	def enter_actions(self):
		self.enemy.speed = 25 + randint(-5, 5)
		self.distance = 0

class EnemyStateBack(State):
	def __init__(self, enemy, map, room):
		State.__init__(self, ENEMY_STATE_TYPE.ENEMY_BACK)
		self.enemy = enemy
		self.map = map
		self.room = room
		self.distance = self.map.width + self.map.height
		self.target = None
		
	def do_actions(self):
		if self.target is not None:
			if not self.enemy.moving:
				location = AStarSearch(self.map, (self.enemy.x, self.enemy.y), self.target)
				if location is not None:
					x, y, distance = getFirstStepAndDistance(location)
					self.enemy.destination = self.map.indexToMapPos(x, y)
					
					self.enemy.moving = True
					direction = getMoveDirection(self.enemy.x, self.enemy.y, x, y)
					if direction is not None:
						self.enemy.entity_surface.updateDirection(direction)
				
				location = AStarSearch(self.map, (self.enemy.x, self.enemy.y), (self.map.hero.x, self.map.hero.y))
				if location is not None:
					hero_x, hero_y, distance = getFirstStepAndDistance(location)				
					self.distance = distance
			else:
				x, y = self.map.MapPosToIndex(self.enemy.destination[0], self.enemy.destination[1])
				direction = getMoveDirection(self.enemy.x, self.enemy.y, x, y)
				if direction is not None:
					self.enemy.entity_surface.updateDirection(direction)
			
	def check_conditions(self):
		if self.distance <= 5:
			print("enemy(%d,%d) back to attack" % (self.enemy.location[0], self.enemy.location[1]))
			return ENEMY_STATE_TYPE.ENEMY_ATTACK
		elif self.enemy.x == self.target[0] and self.enemy.y == self.target[1]:
			return ENEMY_STATE_TYPE.ENEMY_IDLE
		return None
	
	def enter_actions(self):
		self.target = (randint(self.room.x, self.room.x+ self.room.width-1), randint(self.room.y, self.room.y+ self.room.height-1))
		self.distance = 0
		print("enemy(%d,%d) back to room(%d, %d)" % (self.enemy.location[0], self.enemy.location[1], self.target[0], self.target[1]))

class EnemyGroup(object):
	def __init__(self):
		self.entities = {}
		self.entity_id = 0
	
	def add_entity(self, entity):
		self.entities[self.entity_id] = entity
		entity.id = self.entity_id
		self.entity_id += 1
	
	def remove_entity(self, entity):
		del self.entites[entity.id]
	
	def get(self, entity_id):
		if entity_id in self.entities:
			return self.entities[entity_id]
		else:
			return None
	
	def process(self, time_passed):
		time_passed_seconds = time_passed / 1000.0
		for entity in self.entities.values():
			entity.process(time_passed_seconds)

	def render(self, surface, screen_show):
		for entity in self.entities.values():
			entity.render(surface, screen_show)
			

class EntitySurface():
	#surface must have four directions
	def __init__(self, surface, animate_rate):
		self.surface = surface
		self.rate = animate_rate
		self.direction = MOVE_DIRECTION.MOVE_RIGHT
		self.image_direct = self.surface[MOVE_DIRECTION.MOVE_RIGHT.value]
		self.image_index = 0
		self.image_num = len(self.image_direct)
		self.image = self.image_direct[self.image_index]
		self.ticks = 0
		self.moving = False

	def updateDirection(self, direction):
		if self.surface[direction.value] != self.image_direct:
			self.image_direct = self.surface[direction.value]
			self.image_index = 0
		self.moving = True
		
	def updateImage(self):
		self.ticks += 1
		if self.ticks == self.rate:
			self.ticks = 0
			self.image_index += 1
			if self.image_index == self.image_num:
				self.image_index = 0
				self.moving = False
		if self.moving:
			self.image = self.image_direct[self.image_index]
		else:
			self.image = self.image_direct[0]
		return self.image
		
class Hero():
	def __init__(self, screen, init_x, init_y, screen_x, screen_y, hero_surface=None):
		if hero_surface is not None:
			self.entity_surface = EntitySurface(hero_surface, 15)
			self.image = self.entity_surface.updateImage()
			self.rect = self.image.get_rect()
			self.width = self.rect.width
			self.height = self.rect.height
		else:
			self.surface = None
			self.width = ENTITY_SIZE
			self.height = ENTITY_SIZE
		self.screen = screen
		self.x = init_x
		self.y = init_y
		self.screen_x = screen_x
		self.screen_y = screen_y		
	
	def move(self, action, screen_show):
		screen_x = self.screen_x + action[0]
		screen_y = self.screen_y + action[1]
		
		if self.entity_surface is not None:
			self.entity_surface.updateDirection(action[2])
		
		if screen_show.checkMovable(screen_x, screen_y, self.width, self.height):
			self.screen_x = screen_x
			self.screen_y = screen_y
			self.x, self.y = screen_show.screenToMapIndex(screen_x, screen_y)
			return True
		return False
	
	def draw(self, screen_show):
		color = (0, 0, 255)
		location_x, location_y = screen_show.getDrawLoaction(self.screen_x, self.screen_y)
		if self.entity_surface is not None:
			self.image = self.entity_surface.updateImage()		
			self.screen.blit(self.image, (location_x, location_y, self.rect.width, self.rect.height))
			
			# draw hero in small map
			small_location_x, small_location_y, small_width, small_height = screen_show.screenToSmallMapRect(self.screen_x, self.screen_y, self.rect.height, self.rect.height)
			pygame.draw.rect(self.screen, color, pygame.Rect(small_location_x, small_location_y, small_width, small_height))
		else:
			pygame.draw.rect(self.screen, color, pygame.Rect(location_x, location_y, ENTITY_SIZE, ENTITY_SIZE))
		

def initHeroSurface():
	hero_img =  pygame.image.load('resource/image/hero.jpg')
	hero_surface = []
	hero_surface_down = []
	hero_surface_down.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(41, 41, 36, 72)), (18,36)))
	hero_surface_down.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(160, 41, 36, 72)), (18,36)))
	hero_surface_down.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(283, 41, 36, 72)), (18,36)))
	hero_surface_down.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(401, 41, 36, 72)), (18,36)))
	
	hero_surface_left = []
	hero_surface_left.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(41, 191, 36, 72)), (18,36)))
	hero_surface_left.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(160, 191, 36, 72)), (18,36)))
	hero_surface_left.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(283, 191, 36, 72)), (18,36)))
	hero_surface_left.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(401, 191, 36, 72)), (18,36)))
	
	hero_surface_right = []
	hero_surface_right.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(41, 341, 36, 72)), (18,36)))
	hero_surface_right.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(160, 341, 36, 72)), (18,36)))
	hero_surface_right.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(283, 341, 36, 72)), (18,36)))
	hero_surface_right.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(401, 341, 36, 72)), (18,36)))
	
	hero_surface_up = []
	hero_surface_up.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(41, 491, 36, 72)), (18,36)))
	hero_surface_up.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(160, 491, 36, 72)), (18,36)))
	hero_surface_up.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(283, 491, 36, 72)), (18,36)))
	hero_surface_up.append(pygame.transform.scale(hero_img.subsurface(pygame.Rect(401, 491, 36, 72)), (18,36)))
	
	hero_surface.append(hero_surface_left)
	hero_surface.append(hero_surface_up)
	hero_surface.append(hero_surface_right)
	hero_surface.append(hero_surface_down)
	
	return hero_surface

def initEnemySurface():
	enemy_img =  pygame.image.load('resource/image/enemy1.png')
	enemy_surface = []
	enemy_surface_down = []
	enemy_surface_down.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(10, 15, 88, 98)), (44,49)))
	enemy_surface_down.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(138, 15, 88, 98)), (44,49)))
	enemy_surface_down.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(266, 15, 88, 98)), (44,49)))
	enemy_surface_down.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(396, 15, 88, 98)), (44,49)))
	
	enemy_surface_left = []
	enemy_surface_left.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(10, 145, 88, 98)), (44,49)))
	enemy_surface_left.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(138, 145, 88, 98)), (44,49)))
	enemy_surface_left.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(266, 145, 88, 98)), (44,49)))
	enemy_surface_left.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(396, 145, 88, 98)), (44,49)))
	
	enemy_surface_right = []
	enemy_surface_right.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(24, 272, 88, 98)), (44,49)))
	enemy_surface_right.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(154, 272, 88, 98)), (44,49)))
	enemy_surface_right.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(284, 272, 88, 98)), (44,49)))
	enemy_surface_right.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(410, 272, 88, 98)), (44,49)))
	
	enemy_surface_up = []
	enemy_surface_up.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(30, 412, 88, 98)), (44,49)))
	enemy_surface_up.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(160, 412, 88, 98)), (44,49)))
	enemy_surface_up.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(286, 412, 88, 98)), (44,49)))
	enemy_surface_up.append(pygame.transform.scale(enemy_img.subsurface(pygame.Rect(416, 412, 88, 98)), (44,49)))
	
	enemy_surface.append(enemy_surface_left)
	enemy_surface.append(enemy_surface_up)
	enemy_surface.append(enemy_surface_right)
	enemy_surface.append(enemy_surface_down)
	
	return enemy_surface
	
def createEnemy(map, enemy_group):
	if map.room_list is not None:
		enemy1_surface = initEnemySurface()
		print(map.room_list)
		for room in map.room_list:
			enemy = Enemy(enemy_group, enemy1_surface, map, room)
			enemy.x = randint(room.x, room.x + room.width - 1)
			enemy.y = randint(room.y, room.y + room.height - 1)
			enemy.location = map.indexToMapPos(enemy.x, enemy.y)
			print("(%d,%d)" % (enemy.x,  enemy.y))
			enemy.brain.set_state(ENEMY_STATE_TYPE.ENEMY_IDLE)
			enemy_group.add_entity(enemy)
			
			