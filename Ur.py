import pygame
import math
import random
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

CLR_BLK = (0, 0, 0)
CLR_WHT = (255, 255, 255)
CLR_BLU = (0, 0, 255)
CLR_RED = (255, 0, 0)
CLR_GRN = (0, 255, 0)
CLR_YLW = (255, 255, 0)
CLR_MGN = (255, 0, 255)
CLR_CYN = (0, 255, 255)

CLR_BG_BRN = (113, 82, 57)
CLR_BG_YLW = (198, 106, 17)
CLR_BG_SPN = (166, 163, 150)




GRID_SZ = 45
SQ_SZ = (45, 45)
BRD_SZ = (8, 3)
	
BRD_OFST = (5, 4*GRID_SZ)


class RoyalUr(ConnectionListener):
	
	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]
		self.my_stones = data["numOfpieces"]
		self.en_stones = data["numOfpieces"]

	def Network_yourTurn(self, data):

		self.turn = data["torf"]
		self.board_sel = [[False for x in range(8)] for y in range(3)]
		if self.turn:
			self.hasRolled = False
			self.hasPlaced = False
		
	def Network_close(self, data):
		exit()

	def Network_disconnected(self, data):
		print("You have lost connection. Game terminated")
		exit()

	def Network_place(self, data):
		# get attributes
		num = data["num"]
		board = data["board"]
		piecesLeft = data["playerpieces"]
		if data["hasPlaced"]:
			self.hasPlaced = True

		if self.num == 0:
			self.my_stones = piecesLeft[0]
			self.en_stones = piecesLeft[1]
		else:
			self.en_stones = piecesLeft[0]
			self.my_stones = piecesLeft[1]

		self.board = board

	def Network_roll(self, data):
		self.slot_mchn = data["rolls"]
		num = data["num"]
		self.move = self.slot_mchn.count(True)
		if data["hasRolled"]:
			self.hasRolled = True
		if self.move == 0 and self.hasRolled and num == self.num:
			connection.Send({"action": "lorTurn", "lorTurn": "lost", "num": self.num})

	def Network_valid(self, data):
		valid = data["moveable"]
		print("valid", valid)
		
		for element in valid:
			self.board_sel[element[1]][element[0]] = True

	def Network_score(self, data):
		player0score = data["player0"]
		player1score = data["player1"]

		if self.num == 0:
			self.my_score = player0score
			self.en_score = player1score
		else:
			self.my_score = player1score
			self.en_score = player0score

	def __init__(self):
		
		# initialization stuff
		pygame.display.init()
		pygame.font.init()
		width, height = 12*GRID_SZ, 11*GRID_SZ
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("Royal Game of Ur")
		self.clock = pygame.time.Clock()
		self.num = None


		# board routes
		self.myRoute = [False for x in range(15)]
		self.enRoute = [False for x in range(15)]

		# board highlight / darken
		self.board_hl = [[False for x in range(8)] for y in range(3)]
		self.board_sel = [[False for x in range(8)] for y in range(3)]
		# board itself
		self.board = [[0 for x in range(8)] for y in range(3)]
		# rolling highlights
		self.roll_hl = False
		
		# left over stones to place
		self.my_stones = -1
		self.en_stones = -1
		
		# slot machine 
		self.slot_mchn = [False for x in range(4)]
		self.move = -1

		# score keeping stuff
		self.my_score = 0
		self.en_score = 0

		# state setters
		self.turn = True
		self.hasRolled = True
		self.hasPlaced = True
		self.justPlaced = 10
		self.my_stn_colour = None
		self.en_stn_colour = None

		self.init_Graphics()

		# Connecting
		address = input("Address of Server: ")
		try:
		    if not address:
		        host, port = "localhost", 8000
		    else:
		        host, port = address.split(":")
		    self.Connect((host, int(port)))

		except:
		    print ("Error Connecting to Server")
		    print ("Usage:", "host:port")
		    print ("e.g.", "localhost:31425")
		    exit()

		self.running=False

		while not self.running:
		    self.Pump()
		    connection.Pump()
		    sleep(0.01)

		#determine attributes from player #
		if self.num==0:
		    self.turn=True
		    self.hasRolled = False
		    self.hasPlaced = False
		    self.my_stn_colour = self.player1stones
		    self.en_stn_colour = self.player2stones
		
		else:
		    self.turn=False
		    self.hasRolled = True
		    self.hasPlaced = True
		    self.my_stn_colour = self.player2stones
		    self.en_stn_colour = self.player1stones





	def init_Graphics(self):

		# highlights
		self.bg = self._rect((GRID_SZ*12+10, GRID_SZ*3+10), CLR_BG_BRN)
		self.hl_valid_tile = self._rect(SQ_SZ, CLR_GRN)
		self.hl_valid_tile.set_alpha(100)
		self.hl_invalid_tile = self._rect(SQ_SZ, CLR_RED)
		self.hl_invalid_tile.set_alpha(100)
		self.hl_cursor_tile = self._rect(SQ_SZ, CLR_WHT)
		self.hl_cursor_tile.set_alpha(100)

		# panels
		self.spin_pnl = self._rect((GRID_SZ*3+30, GRID_SZ*3), CLR_BG_SPN)
		self.spin_pnl.set_alpha(191)
		self.me_pnl = self._rect((GRID_SZ*12, GRID_SZ*4), CLR_WHT)
		self.me_pnl.set_alpha(191)
		self.en_pnl = self._rect((GRID_SZ*12, GRID_SZ*4), CLR_BLK)
		self.en_pnl.set_alpha(191)
		self.roll_pnl = self._rect((135, 35), CLR_GRN)
		self.rolled_pnl = self._rect((135, 35), CLR_RED)
		self.roll_btn_hl = self._rect((135, 35), CLR_WHT)
		self.roll_btn_hl.set_alpha(100)
		self.roll_btn_no = self._rect((135, 35), CLR_RED)
		self.roll_btn_no.set_alpha(100)


		# images
		self.rosette = pygame.image.load("assets/Rosette.png")
		self.tiles = pygame.image.load("assets/Tiles.png")
		self.grid = pygame.image.load("assets/Grid.png")
		self.largeTiles = pygame.image.load("assets/LargeTiles.png")
		self.eyes = pygame.image.load("assets/Eyes.png")
		self.circles = pygame.image.load("assets/Circles.png")
		self.player1stones = pygame.image.load("assets/Player1Stones.png")
		self.player2stones = pygame.image.load("assets/Player2Stones.png")
		self.one = pygame.image.load("assets/One.png")
		self.zero = pygame.image.load("assets/Zero.png")

		
	def _rect(self, size, fill):
		surface = pygame.Surface(size)
		surface.fill(fill)
		return surface

		


	def draw_Board(self):

		# blue background
		self.screen.blit(self.bg, [BRD_OFST[0] - 5, BRD_OFST[1] - 5])

		for i in range(8):
			for j in range(3):
				
				# condensing
				coordinates = [i*GRID_SZ + BRD_OFST[0], j*GRID_SZ + BRD_OFST[1]]

				# rosette 
				if ((i == 0 or i ==6) and (j == 0 or j == 2) or (i == 3 and j == 1)):
					self.screen.blit(self.rosette, coordinates)
				# eyes
				elif ((i == 1 or i == 3) and (j == 0 or j == 2) or (i == 6 and j == 1)):
					self.screen.blit(self.eyes, coordinates)
				# grids
				elif (i == 0 and j == 1):
					self.screen.blit(self.grid, coordinates)
				# tiles
				elif ((i == 2 or i == 5) and (j == 1)):
					self.screen.blit(self.tiles, coordinates)
				# large tiles
				elif ((i == 7) and (j == 0 or j == 2)):
					self.screen.blit(self.largeTiles, coordinates)
				# empty 
				elif ((i == 4 or i == 5) and (j == 0 or j == 2)):
					pass
				# circles
				else:
					self.screen.blit(self.circles, coordinates)

				if self.board_hl[j][i] and (j != 0 and ((i != 4 and i != 5) or j != 2)):
					self.screen.blit(self.hl_cursor_tile, coordinates)

				if self.board[j][i] == 1:
					self.screen.blit(self.player1stones, coordinates)
				elif self.board[j][i] == 2:
					self.screen.blit(self.player2stones, coordinates)

				if self.board_sel[j][i]:
					self.screen.blit(self.hl_valid_tile, coordinates)

		
		for i in range(4):
			for j in range(2):
				my_coord = [i*GRID_SZ + BRD_OFST[0], (j+3)*GRID_SZ + BRD_OFST[1]+5]
				en_coord = [i*GRID_SZ + BRD_OFST[0], (-j-1)*GRID_SZ + BRD_OFST[1]-5]

				if (2*i + j < self.my_stones):
					self.screen.blit(self.my_stn_colour, my_coord)

				if (2*i + j < self.en_stones):
					self.screen.blit(self.en_stn_colour, en_coord)


		for x in range(14):
			if self.myRoute[x]:
				my_stn_coord = [BRD_OFST[0] + MY_PATH[x][0]*GRID_SZ, BRD_OFST[1] + MY_PATH[x][1]*GRID_SZ]
				self.screen.blit(self.player1stones, my_stn_coord)

			if self.enRoute[x]:
				en_stn_coord = [BRD_OFST[0] + EN_PATH[x][0]*GRID_SZ, BRD_OFST[1] + EN_PATH[x][1]*GRID_SZ]
				self.screen.blit(self.player2stones, en_stn_coord)

	def draw_Stats(self):
		
		# fonts
		font32 = pygame.font.SysFont(None, 32)
		font128 = pygame.font.SysFont(None, 120)
		font20 = pygame.font.SysFont(None, 20)

		# labels
		me_label = font32.render("You", 1, CLR_WHT)
		en_label = font32.render("Enemy", 1, CLR_WHT)
		roll_lbl = font32.render("Roll", 1, CLR_GRN)
		me_score = font128.render(str(self.my_score), 1, CLR_WHT)
		en_score = font128.render(str(self.en_score), 1, CLR_WHT)


		# panels
		self.screen.blit(self.spin_pnl, (BRD_OFST[0] + 8*GRID_SZ + 5, BRD_OFST[1]))

		if self.hasRolled:
			self.screen.blit(self.rolled_pnl, (BRD_OFST[0]+8*GRID_SZ + 20, BRD_OFST[1] + 2*GRID_SZ + 5))
		else:
			self.screen.blit(self.roll_pnl, (BRD_OFST[0]+8*GRID_SZ + 20, BRD_OFST[1] + 2*GRID_SZ + 5))

		# draw labels
		self.screen.blit(me_label, (BRD_OFST[0], 11*GRID_SZ-32))
		self.screen.blit(en_label, (BRD_OFST[0], 10))
		self.screen.blit(me_score, (BRD_OFST[0] + 6*GRID_SZ, 7*GRID_SZ + 10))
		self.screen.blit(en_score, (BRD_OFST[0] + 6*GRID_SZ, 2*GRID_SZ))

		# draw slot machine
		for x in range(4):
			slot_mchn_coord = (BRD_OFST[0]+8*GRID_SZ + 20 + x*35, BRD_OFST[1] + 1*GRID_SZ)
			this = self.one if self.slot_mchn[x] else self.zero
			self.screen.blit(this, slot_mchn_coord)

		if self.roll_hl:
			if self.hasRolled:
				self.screen.blit(self.roll_btn_no, (BRD_OFST[0]+8*GRID_SZ + 20, BRD_OFST[1] + 2*GRID_SZ + 5))
			else:
				self.screen.blit(self.roll_btn_hl, (BRD_OFST[0]+8*GRID_SZ + 20, BRD_OFST[1] + 2*GRID_SZ + 5))

	def update(self):

		self.justPlaced -= 1

		# connection stuff

		connection.Pump()
		self.Pump()

		# sleeps to make the game 60 fps
		self.clock.tick(60)

		# clears the screen
		self.screen.fill(CLR_BG_YLW)
		self.draw_Board()
		self.draw_Stats()

		# grab mouse positions
		mouse = pygame.mouse.get_pos()

		# convert them to grids
		bx = int(math.ceil((mouse[0]-BRD_OFST[0])/45.0))-1
		by = int(math.ceil((mouse[1]-BRD_OFST[1])/45.0))-1
		in_board = False

		roll_box = (BRD_OFST[0]+8*GRID_SZ + 20, BRD_OFST[1] + 2*GRID_SZ)

		if roll_box[0] < mouse[0] < roll_box[0] + 135 and roll_box[1] < mouse[1] < roll_box[1] + 35:
			self.roll_hl = True
		else:
			self.roll_hl = False

		# check if in bound 
		if -1 < bx < BRD_SZ[0] and 0 < by < BRD_SZ[1] and ((bx != 4 and bx != 5) or by != 2):
			in_board = True

		# reset all highlights
		for x in range(BRD_SZ[0]):
			for y in range(BRD_SZ[1]):
				self.board_hl[y][x] = False

		# show highlighted grid of mouse if in bound
		if in_board:
			self.board_hl[by][bx] = True

		for event in pygame.event.get():
			# quits if the quit button is pressed
			if event.type == pygame.QUIT:
				exit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if (in_board and self.turn and self.justPlaced <= 0 and 
					self.move > 0 and self.board_hl[by][bx] and self.board_sel[by][bx]) and not self.hasPlaced:
					self.justPlaced = 10
					connection.Send({"action": "place", "x": bx, "y": by, "num": self.num, "move": self.move})

				if self.roll_hl and self.turn and self.justPlaced <= 0:
					connection.Send({"action": "roll", "num": self.num, "hasRolled": self.hasRolled})
					self.justPlaced = 10

		# update the screen
		pygame.display.flip()


ur = RoyalUr()
while 1:
	ur.update()
