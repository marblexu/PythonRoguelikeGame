import pygame
from pygame.locals import *
from sys import exit
from random import randint
from GameMap import *
from MazeGenerator import *
from AStarSearch import *
from RogueLikeMaze import *
from GameRole import *

FRAME_RATE = 60
HERO_SPEED = 1
		
class Button():
	def __init__(self, screen, type, x, y):
		self.screen = screen
		self.width = BUTTON_WIDTH
		self.height = BUTTON_HEIGHT
		self.button_color = (128,128,128)
		self.text_color = [(0,255,0), (255,0,0)]
		self.font = pygame.font.SysFont(None, BUTTON_HEIGHT*2//3)
		
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.topleft = (x, y)
		self.type = type
		self.init_msg()
		
	def init_msg(self):
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[0], self.button_color)
		self.msg_image_rect = self.msg_image.get_rect()
		self.msg_image_rect.center = self.rect.center
		
	def draw(self):
		self.screen.fill(self.button_color, self.rect)
		self.screen.blit(self.msg_image, self.msg_image_rect)
	
	def click(self, game):
		game.maze_type = self.type
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[1], self.button_color)
	
	def unclick(self):
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[0], self.button_color)

class Game():
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode([SCREEN_WIDTH + MAPS_INTERVAL + SMALL_MAP_WIDTH + MAPS_INTERVAL, SCREEN_HEIGHT + BUTTON_HEIGHT])
		self.clock = pygame.time.Clock()
		self.map = Map(REC_X_NUM, REC_Y_NUM)
		self.screen_show = ScreenShow(SCREEN_WIDTH, SCREEN_HEIGHT, 0, BUTTON_HEIGHT, self.map)
		self.enemy_group = EnemyGroup()
		self.mode = 0
		self.buttons = []
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RECURSIVE_BACKTRACKER, 0, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RANDOM_PRIM, BUTTON_WIDTH + 10, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RECURSIVE_DIVISION, (BUTTON_WIDTH + 10) * 2, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.UNION_FIND_SET, (BUTTON_WIDTH + 10) * 3, 0))
		self.buttons[0].click(self)
		self.hero = None
		self.tick = 0
		
	def play(self):
		def checkBulletCollide(enemy_group, bullets_group):
			score = 0
			#for group in enemy_group:
			#	for bullet_group in bullets_group:
			#		score += group.checkBulletCollide(bullet_group) 
			return score

		time_passed = self.clock.tick(FRAME_RATE)		

		pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(0, 0, SCREEN_WIDTH, BUTTON_HEIGHT))
		for button in self.buttons:
			button.draw()

		self.tick += 1
		if self.tick == FRAME_RATE:
			self.tick = 0
			
		if self.hero is not None:
			if self.hero.shouldShoot():
				self.hero.shootWeapon(self.screen_show)
			elif action is not None and self.tick % HERO_SPEED == 0:
				if self.hero.move(action, self.screen_show):
					self.screen_show.updateOffset(self.hero, action)
					x, y = self.screen_show.mapToMapIndex(self.hero.map_x, self.hero.map_y)
					self.map.clearFrog(x, y, 5)
			checkBulletCollide(self.enemy_group, self.hero.weapon_groups)
			
		self.screen_show.drawBackground(self.screen)
		
		if self.hero is not None:
			for weapon_group in self.hero.weapon_groups:
				weapon_group.update()
				weapon_group.draw(self.screen)
			self.hero.draw(self.screen_show)
		self.enemy_group.process(time_passed)
		self.enemy_group.render(self.screen, self.screen_show)

			
	def generateMaze(self):
		if self.mode >= 9:
			self.mode = 0
		if self.mode == 0:
			self.map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)
			room_max_size = self.map.width//10 if self.map.width < self.map.height else self.map.height//10
			ROOM_NUM = room_max_size*20
			addRooms(self.map, ROOM_NUM, room_max_size)
			print(MOVE_DIRECTION.MOVE_RIGHT.value)
		elif self.mode == 1:
			growMaze(self.map, (self.map.width-1)//2, (self.map.height-1)//2)
			
		elif self.mode == 2:
			connectRegions(self.map, (self.map.width-1)//2, (self.map.height-1)//2)
		elif self.mode == 3:
			addReduentConnect(self.map, (self.map.width-1)//2, (self.map.height-1)//2, 8)
		elif self.mode == 4:
			removeDeadEnds(self.map, (self.map.width-1)//2, (self.map.height-1)//2)
		elif self.mode == 5:
			self.map.resetFrog(1)
		elif self.mode == 6:
			self.source = self.map.generateEntityPos((1,self.map.width//5),(1, self.map.height//5))
			screen_x, screen_y = self.screen_show.mapIndexToScreen(self.source[0], self.source[1])
			hero_surface = initHeroSurface()
			weapon_groups = initWeaponGroups()
			self.hero = Hero(self.screen, self.source[0], self.source[1], screen_x, screen_y, weapon_groups, hero_surface)
			print("hero(%d,%d)" % (self.source[0], self.source[1]))
			self.dest = self.map.generateEntityPos((self.map.width*4//5, self.map.width-2), (1, self.map.height-2))
			self.map.clearFrog(self.source[0], self.source[1], 5)
			self.map.clearFrog(self.dest[0], self.dest[1], 0)
			#self.map.setMap(self.source[0], self.source[1], MAP_ENTRY_TYPE.MAP_TARGET)
			
			self.map.setMap(self.dest[0], self.dest[1], MAP_ENTRY_TYPE.MAP_TARGET)
		elif self.mode == 7:	
			createEnemy(self.screen_show, self.map, self.enemy_group, self.hero)
		#	AStarSearch(self.map, self.source, self.dest)
		#	self.map.setMap(self.source[0], self.source[1], MAP_ENTRY_TYPE.MAP_TARGET)
		#	self.map.setMap(self.dest[0], self.dest[1], MAP_ENTRY_TYPE.MAP_TARGET)
		else:
			self.map.resetMap(MAP_ENTRY_TYPE.MAP_EMPTY)
			self.map.resetFrog(0)
			self.hero = None
		self.mode += 1

def check_buttons(game, mouse_x, mouse_y):
	for button in game.buttons:
		if button.rect.collidepoint(mouse_x, mouse_y):
			button.click(game)
			for tmp in game.buttons:
				if tmp != button:
					tmp.unclick()
			break

offset = {pygame.K_LEFT:(-1, 0, MOVE_DIRECTION.MOVE_LEFT), 
		  pygame.K_RIGHT: (1, 0, MOVE_DIRECTION.MOVE_RIGHT), 
		  pygame.K_UP:(0, -1, MOVE_DIRECTION.MOVE_UP), 
		  pygame.K_DOWN:(0, 1, MOVE_DIRECTION.MOVE_DOWN)}

game = Game()
action = None

while True:
	game.play()
	pygame.display.update()
		
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key in offset:
				action = offset[event.key]
			elif event.key == pygame.K_SPACE:
				game.generateMaze()
				break
			elif event.key == pygame.K_x:
				if game.hero is not None:
					game.hero.setShoot()
		elif event.type == pygame.KEYUP:
			if event.key in offset:
				action = None
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_buttons(game, mouse_x, mouse_y)
		
