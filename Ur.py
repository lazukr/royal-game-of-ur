import pygame
import math
import random
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep


RGB = {
	"BLK": (0, 0, 0),
	"WHT": (255, 255, 255),
	"BLU": (0, 0, 255),
	"RED": (255, 0, 0),
	"GRN": (0, 255, 0),
	"YLW": (255, 255, 0),
	"BG_BRN": (113, 82, 57),
	"BG_YLW": (198, 106, 17),
	"BG_SPN": (166, 163, 150)
}


GRID = 45
SQUARE = (GRID, GRID)
BOARD = (8, 3)
RECT = (135, 35)
WINDOW_WIDTH = 12*GRID
WINDOW_HEIGHT = 11*GRID
BOARD_OFFSET = (5, 4*GRID)


class RoyalUr(ConnectionListener):
	
	def Network_startgame(self, data):
		self.running = True
		self.player_num = data["player"]
		self.my_stones = data["numOfpieces"]
		self.en_stones = data["numOfpieces"]
		self.my_score = 0
		self.en_score = 0

	def Network_yourTurn(self, data):

		self.turn = data["torf"]
		self.board_select = [[False for x in range(8)] for y in range(3)]
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

		if self.player_num == 0:
			self.my_stones = piecesLeft[0]
			self.en_stones = piecesLeft[1]
		else:
			self.en_stones = piecesLeft[0]
			self.my_stones = piecesLeft[1]

		self.board = board

	def Network_roll(self, data):
		self.slot_machine = data["rolls"]
		num = data["num"]
		self.move = self.slot_machine.count(True)
		if data["hasRolled"]:
			self.hasRolled = True
		if self.move == 0 and self.hasRolled and num == self.player_num:
			connection.Send({"action": "lorTurn", "lorTurn": "lost", "num": self.player_num})

	def Network_valid(self, data):
		valid = data["moveable"]
		print("valid", valid)
		
		for x, y in valid:
			self.board_select[y][x] = True

	def Network_score(self, data):
		player0score = data["player0"]
		player1score = data["player1"]

		if self.player_num == 0:
			self.my_score = player0score
			self.en_score = player1score
		else:
			self.my_score = player1score
			self.en_score = player0score

	def __init__(self):
		
		# initialization stuff
		pygame.display.init()
		pygame.font.init()

		self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption("Royal Game of Ur")

		self.clock = pygame.time.Clock()

		# board highlight / select
		self.board_highlight = [[False for x in range(8)] for y in range(3)]
		self.board_select = [[False for x in range(8)] for y in range(3)]

		# board itself
		self.board = [[0 for x in range(8)] for y in range(3)]

		# slot machine 
		self.slot_machine = [False for x in range(4)]
		
		self.player_num = None
		# left over stones to place
		self.my_stones = -1
		self.en_stones = -1
		
		
		self.move = -1

		# score keeping stuff
		self.my_score = -1
		self.en_score = -1

		# state setters
		self.roll_highlight = False
		self.turn = True
		self.hasRolled = True
		self.hasPlaced = True
		self.justPlaced = 10


		self.stone_colour = [None in range(2)]
		self.my_stone_colour = None
		self.en_stone_colour = None

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
		if self.player_num==0:
		    self.turn=True
		    self.hasRolled = False
		    self.hasPlaced = False
		    self.my_stone_colour = self.player1stones
		    self.en_stone_colour = self.player2stones
		
		else:
		    self.turn=False
		    self.hasRolled = True
		    self.hasPlaced = True
		    self.my_stone_colour = self.player2stones
		    self.en_stone_colour = self.player1stones





	def init_Graphics(self):

		# panels
		self.panel = self._rect((GRID*12+10, GRID*3+10), RGB["BG_BRN"])
		self.spin_panel = self._rect((GRID*3+30, GRID*3), RGB["BG_SPN"])
		self.spin_panel.set_alpha(191)

		# cursor highlights
		self.highlight_valid_tile = self._rect(SQUARE, RGB["GRN"])
		self.highlight_cursor_tile = self._rect(SQUARE, RGB["WHT"])
		self.highlight_valid_tile.set_alpha(100)
		self.highlight_cursor_tile.set_alpha(100)

		# roll states
		self.roll_button = self._rect(RECT, RGB["GRN"])
		self.rolled_button = self._rect(RECT, RGB["RED"])

		# roll highlights
		self.roll_btn_greenlight = self._rect(RECT, RGB["WHT"])
		self.roll_btn_redlight = self._rect(RECT, RGB["RED"])
		self.roll_btn_greenlight.set_alpha(100)
		self.roll_btn_redlight.set_alpha(100)

		# images
		self.rosette = pygame.image.load("assets/Rosette.png")
		self.tiles = pygame.image.load("assets/Tiles.png")
		self.grid = pygame.image.load("assets/Grid.png")
		self.largeTiles = pygame.image.load("assets/LargeTiles.png")
		self.eyes = pygame.image.load("assets/Eyes.png")
		self.circles = pygame.image.load("assets/Circles.png")
		self.board_display = pygame.image.load("assets/Board.png")
		self.player1stones = pygame.image.load("assets/Player1Stones.png")
		self.player2stones = pygame.image.load("assets/Player2Stones.png")
		self.one = pygame.image.load("assets/One.png")
		self.zero = pygame.image.load("assets/Zero.png")

		# fonts
		self.font32 = pygame.font.SysFont(None, 32)
		self.font120 = pygame.font.SysFont(None, 120)

		# static labels
		me_label = self.font32.render("You", 1, RGB["WHT"])
		en_label = self.font32.render("Enemy", 1, RGB["WHT"])

		# static screen
		self.static_screen = self._rect((WINDOW_WIDTH, WINDOW_HEIGHT), RGB["BG_YLW"])
		self.static_screen.blit(self.panel, [BOARD_OFFSET[0] - 5, BOARD_OFFSET[1] - 5])
		self.static_screen.blit(self.board_display, BOARD_OFFSET)
		self.static_screen.blit(self.spin_panel, (BOARD_OFFSET[0] + 8*GRID + 5, BOARD_OFFSET[1]))
		self.static_screen.blit(me_label, (BOARD_OFFSET[0], 11*GRID-32))
		self.static_screen.blit(en_label, (BOARD_OFFSET[0], 10))
		print("diplsay initialization complete")
		
	def _rect(self, size, fill):
		surface = pygame.Surface(size)
		surface.fill(fill)
		return surface

		


	def draw_Board(self):

		for i in range(8):
			for j in range(3):
				
				# condensing
				coordinates = [i*GRID + BOARD_OFFSET[0], j*GRID + BOARD_OFFSET[1]]

				if self.board_highlight[j][i] and (j != 0 and ((i != 4 and i != 5) or j != 2)):
					self.screen.blit(self.highlight_cursor_tile, coordinates)

				if self.board[j][i] == 1:
					self.screen.blit(self.player1stones, coordinates)
				elif self.board[j][i] == 2:
					self.screen.blit(self.player2stones, coordinates)

				if self.board_select[j][i]:
					self.screen.blit(self.highlight_valid_tile, coordinates)

		
		for i in range(4):
			for j in range(2):
				my_coord = [i*GRID + BOARD_OFFSET[0], (j+3)*GRID + BOARD_OFFSET[1]+5]
				en_coord = [i*GRID + BOARD_OFFSET[0], (-j-1)*GRID + BOARD_OFFSET[1]-5]

				if (2*i + j < self.my_stones):
					self.screen.blit(self.my_stone_colour, my_coord)

				if (2*i + j < self.en_stones):
					self.screen.blit(self.en_stone_colour, en_coord)

	def draw_Stats(self):

		# scores
		me_score = self.font120.render(str(self.my_score), 1, RGB["WHT"])
		en_score = self.font120.render(str(self.en_score), 1, RGB["WHT"])

		# draw scores
		self.screen.blit(me_score, (BOARD_OFFSET[0] + 6*GRID, 7*GRID + 10))
		self.screen.blit(en_score, (BOARD_OFFSET[0] + 6*GRID, 2*GRID))

		# draw slot machine
		for x in range(4):
			slot_machine_coord = (BOARD_OFFSET[0]+8*GRID + 20 + x*35, BOARD_OFFSET[1] + 1*GRID)
			this = self.one if self.slot_machine[x] else self.zero
			self.screen.blit(this, slot_machine_coord)

		# roll button colour
		roll_coord = (BOARD_OFFSET[0]+8*GRID + 20, BOARD_OFFSET[1] + 2*GRID + 5)
		if self.hasRolled:
			self.screen.blit(self.rolled_button, roll_coord)
		else:
			self.screen.blit(self.roll_button, roll_coord)

		# highlight rolling coordinates
		if self.roll_highlight:
			if self.hasRolled:
				self.screen.blit(self.roll_btn_redlight, roll_coord)
			else:
				self.screen.blit(self.roll_btn_greenlight, roll_coord)

	def update(self):

		self.justPlaced -= 1

		# connection stuff

		connection.Pump()
		self.Pump()

		# sleeps to make the game 60 fps
		self.clock.tick(60)

		# clears the screen
		self.screen.blit(self.static_screen, (0,0))
		self.draw_Board()
		self.draw_Stats()

		# grab mouse positions
		mouse = pygame.mouse.get_pos()

		# convert them to grids
		bx = int(math.ceil((mouse[0]-BOARD_OFFSET[0])/45.0))-1
		by = int(math.ceil((mouse[1]-BOARD_OFFSET[1])/45.0))-1
		in_board = False

		roll_box = (BOARD_OFFSET[0]+8*GRID + 20, BOARD_OFFSET[1] + 2*GRID)

		if roll_box[0] < mouse[0] < roll_box[0] + 135 and roll_box[1] < mouse[1] < roll_box[1] + 35:
			self.roll_highlight = True
		else:
			self.roll_highlight = False

		# check if in bound 
		if -1 < bx < BOARD[0] and 0 < by < BOARD[1] and ((bx != 4 and bx != 5) or by != 2):
			in_board = True

		# reset all highlights
		for x in range(BOARD[0]):
			for y in range(BOARD[1]):
				self.board_highlight[y][x] = False

		# show highlighted grid of mouse if in bound
		if in_board:
			self.board_highlight[by][bx] = True

		for event in pygame.event.get():
			# quits if the quit button is pressed
			if event.type == pygame.QUIT:
				exit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				print("REGISTERED MOUSEBUTTONDOWN EVENT")
				if (in_board and self.turn and self.justPlaced <= 0 and 
					self.move > 0 and self.board_highlight[by][bx] and 
					self.board_select[by][bx]) and not self.hasPlaced:
					print("ATTEMPTING TO PLACE IN GRID: ", bx, by)
					self.justPlaced = 10
					connection.Send({"action": "place", "x": bx, "y": by, "num": self.player_num, "move": self.move})
					print("PLACE IN GRID SENT")

				if self.roll_highlight and self.turn and self.justPlaced <= 0:
					print("ATTEMPTING TO ROLL")
					connection.Send({"action": "roll", "num": self.player_num, "hasRolled": self.hasRolled})
					print("ATTEMPTING TO ROLL SENT")
					self.justPlaced = 10

		# update the screen
		pygame.display.flip()


ur = RoyalUr()
while 1:
	ur.update()
