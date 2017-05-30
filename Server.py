from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
import random

# these paths are used to map the swirl path the 
# stones are to take compared to the grid board

PTOG = {
	"m0" : (3, 2),
	"m1" : (2, 2),
	"m2" : (1, 2),
	"m3" : (0, 2),
	"m4" : (0, 1),
	"m5" : (1, 1),
	"m6" : (2, 1),
	"m7" : (3, 1),
	"m8" : (4, 1),
	"m9" : (5, 1),
	"m10" : (6, 1),
	"m11" : (7, 1),
	"m12" : (7, 2),
	"m13" : (6, 2),
	"e0" : (3, 0),
	"e1" : (2, 0),
	"e2" : (1, 0),
	"e3" : (0, 0),
	"e4" : (0, 1),
	"e5" : (1, 1),
	"e6" : (2, 1),
	"e7" : (3, 1),
	"e8" : (4, 1),
	"e9" : (5, 1),
	"e10" : (6, 1),
	"e11" : (7, 1),
	"e12" : (7, 0),
	"e13" : (6, 0)
}

GTOP = {
	"00": ("e", 3),
	"01": ("e", 2),
	"02": ("e", 1),
	"03": ("e", 0),
	"06": ("e", 13),
	"07": ("e", 12),
	"10": ("b", 4),
	"11": ("b", 5),
	"12": ("b", 6),
	"13": ("b", 7),
	"14": ("b", 8),
	"15": ("b", 9),
	"16": ("b", 10),
	"17": ("b", 11),
	"20": ("m", 3),
	"21": ("m", 2),
	"22": ("m", 1),
	"23": ("m", 0),
	"26": ("m", 13),
	"27": ("m", 12)
}

rosette = ["00", "02", "31", "60", "62"]
NUM_OF_STONES = 1

class ClientChannel(Channel):

	def __init__(self, *args, **kwargs):
		Channel.__init__(self, *args, **kwargs)

	def Network(self, data):
		print(data)
		pass

	def Network_place(self, data):
		x = data["x"]
		y = data["y"]
		num = data["num"]
		move = data["move"]
		self._server.placeStone(x, y, data, num, move)

	def Network_roll(self, data):
		hasRolled = data["hasRolled"]
		num = data["num"]
		self._server.roll(hasRolled, data, num)

	def Network_lorTurn(self, data):
		lorTurn = data["lorTurn"]
		num = data["num"]
		self._server.lorTurn(lorTurn, num)

class UrServer(Server):
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		print("Server launched")
		self.game = None
		self.ongoingGame = None


	def Connected(self, channel, addr):
		print("new connection: ", channel)

		if self.game == None:
			self.game = Game(channel)
			print("connection", channel)

		else:
			self.game.players[1] = channel
			for x in range(2):
				self.game.players[x].Send({"action": "startgame","player":x, "numOfpieces": NUM_OF_STONES})
			# self.game.player0.Send({"action": "startgame","player":0, "numOfpieces": NUM_OF_STONES})
			# self.game.player1.Send({"action": "startgame","player":1, "numOfpieces": NUM_OF_STONES})
			self.ongoingGame = self.game
			self.game = None

	def placeStone(self, x, y, data, num, move):
		if self.ongoingGame != None:
			self.ongoingGame.placeStone(x, y, data, num, move)

	def roll(self, hasRolled, data, num):
		if self.ongoingGame != None:
			self.ongoingGame.roll(hasRolled, data, num)

	def lorTurn(self, lorTurn, num):
		if self.ongoingGame != None:
			self.ongoingGame.lorTurn(lorTurn, num)


	def launch(self):
		while True:
			self.Pump()
			sleep(0.01)

class Game:
	def __init__(self, player0):
		# whose turn
		self.turn = 0

		# board
		self.boards = [[[0 for x in range(8)] for y in range(3)] for z in range(2)]

		self.board = [[0 for x in range(8)] for y in range(3)]
		self.board_alt = [[0 for x in range(8)] for y in range(3)]
		self.slt_mchn = [False for x in range(4)]
		# 0th is player 0, 1 in player 1
		self.playerpaths = [[False for x in range(15)] for y in range(2)]
		self.playerpieces = [NUM_OF_STONES, NUM_OF_STONES]
		self.playerscores = [0, 0]
		self.move = -1

		# initialize players
		self.players = [player0, None]
		self.player0 = player0
		self.player1 = None


	def placeStone(self, x, y, data, num, move):
		
		# does a horizontal reflection for coordinates due to the flip display
		# on enemy screens
		real_y = y

		# checks for flipped coordinates and converts it to a standard coordinate
		# this standard coordinate follows player0's perspective
		if num == 1 and (real_y == 0 or real_y == 2):
			real_y = 2 if y == 0 else 0


		# check if it's the player's turn
		if num == self.turn:

			path_pos = GTOP[str(real_y) + str(x)][1]

			ycoord = [y, y]
			if y != 1:
				ycoord[1] = 2 if y == 0 else 0


			# placing new piece
			if (self.board[real_y][x] == 0 and 
				self.playerscores[num] + self.playerpaths[num].count(True) < NUM_OF_STONES):

				# place new piece

				# update hasPlaced variable, if true, the player cannot roll again
				# this prevents re-rolls
				playersHasPlaced = [None, None]
				playersHasPlaced[num] = True

				# relays the x, y coordinate that the stone has successfully been placed
				# due to the flipped y for the case of player1, we consider cases when its
				# player0 or player1 playing
				# this also relays the hasPlaced variable
				# uses num to figure out which stone to work with,
				# bitwise or to figure out alternate
				self.playerpaths[num][GTOP[str(y)+str(x)][1]] = True
				self.playerpieces[num] -= 1
				self.board[ycoord[num]][x] = num + 1
				self.board_alt[ycoord[num^1]][x] = num + 1

				for x in range(2):
					self.players[x].Send({"action": "place", "board": self.board, "num": num,
						"hasPlaced": playersHasPlaced[x], "playerpieces": self.playerpieces})
				# self.player0.Send({"action": "place", "board": self.board, "num": num,
				# 		"hasPlaced": playersHasPlaced[0], "playerpieces": self.playerpieces})
				# self.player1.Send({"action": "place", "board": self.board_alt,"num": num, 
				# 		"hasPlaced": playersHasPlaced[1], "playerpieces": self.playerpieces})

				# allow the next turn
				if str(x) + str(y) not in rosette:
						self.turn = 0 if self.turn else 1
				self._nextTurn(self.turn)
			

			# check if the stone does exist in that position according to the server
			# and the planned move is not over the maximum
			elif self.playerpaths[num][path_pos] and path_pos + move < 14:

				# finds right label for PTOG conversion
				label = "m" if num == 0 else "e"
				(new_x, new_y) = PTOG[label + str(path_pos + move)]
				print("new pos: ", new_x, new_y)

				new_ycoord = [new_y, new_y]
				if new_y != 1:
					new_ycoord[1] = 2 if new_y == 0 else 0

				playersHasPlaced = [None, None]
				playersHasPlaced[num] = True

				# trivial case if the board spot is empty
				if self.board[new_y][new_x] == 0:

					# update the paths
					self.playerpaths[num][GTOP[str(new_y)+str(new_x)][1]] = True
					self.playerpaths[num][GTOP[str(y)+str(x)][1]] = False
					
					# update the coordinates
					self.board[ycoord[num]][x] = 0
					self.board_alt[ycoord[num^1]][x] = 0

					self.board[new_ycoord[0]][new_x] = num + 1
					self.board_alt[new_ycoord[1]][new_x] = num + 1
				
					for x in range(2):
						self.players[x]..Send({"action": "place", "board": self.board, "num": num,
						"hasPlaced": playersHasPlaced[x], "playerpieces": self.playerpieces})
					# self.player0.Send({"action": "place", "board": self.board, "num": num,
					# 	"hasPlaced": playersHasPlaced[0], "playerpieces": self.playerpieces})
					# self.player1.Send({"action": "place", "board": self.board_alt, "num": num, 
					# 	"hasPlaced": playersHasPlaced[1], "playerpieces": self.playerpieces})

					# allow the next turn if not rosette, else go again
					if str(new_x) + str(new_y) not in rosette:
						self.turn = 0 if self.turn else 1

					self._nextTurn(self.turn)
					

				# not empty
				elif self.board[new_y][new_x] != num + 1 and str(new_x) + str(new_y) not in rosette:

					self.board[new_ycoord[0]][new_x] = num + 1
					self.board_alt[new_ycoord[1]][new_x] = num + 1
					self.board[ycoord[num]][x] = 0
					self.board_alt[ycoord[num^1]][x] = 0
					self.playerpaths[num][GTOP[str(new_y)+str(new_x)][1]] = True
					self.playerpaths[num][GTOP[str(y)+str(x)][1]] = False
					self.playerpieces[num^1] += 1
					self.playerpaths[num^1][GTOP[str(new_y)+str(new_x)][1]] = False

					for x in range(2):
						self.players[x].Send({"action": "place", "board": self.board, "num": num,
						"hasPlaced": playersHasPlaced[x], "playerpieces": self.playerpieces})

					self.player0.Send({"action": "place", "board": self.board, "num": num,
						"hasPlaced": playersHasPlaced[0], "playerpieces": self.playerpieces})
					self.player1.Send({"action": "place", "board": self.board_alt,"num": num, 
						"hasPlaced": playersHasPlaced[1], "playerpieces": self.playerpieces})

					# allow the next turn
					self.turn = 0 if self.turn else 1
					self._nextTurn(self.turn)

			elif self.playerpaths[num][path_pos] and path_pos + move == 14:
				# updates turns
				self.turn = 0 if self.turn else 1

				self.playerpaths[num][GTOP[str(y)+str(x)][1]] = False
				self.playerscores[num] += 1
				self.board[ycoord[num]][x] = 0
				self.board_alt[ycoord[num^1]][x] = 0
				playersHasPlaced = [None, None]
				playersHasPlaced[num] = True				

				self.player0.Send({"action": "place", "board": self.board, "num": num,
						"hasPlaced": playersHasPlaced[0], "playerpieces": self.playerpieces})
				self.player1.Send({"action": "place", "board": self.board_alt,"num": num, 
						"hasPlaced": playersHasPlaced[1], "playerpieces": self.playerpieces})

				if self.playerscores[num] == NUM_OF_STONES:



				else:

					self.player0.Send({"action": "score", "player0": self.playerscores[0],
						"player1": self.playerscores[1]})
					self.player1.Send({"action": "score", "player0": self.playerscores[0],
						"player1": self.playerscores[1]})
					# allow the next turn
					self._nextTurn(self.turn)

	def lorTurn(self, lorTurn, num):
		print(lorTurn)

		# if turn is lost, then give turn to enemy
		if num == self.turn and lorTurn == "lost":
			self.turn = 0 if self.turn else 1

		self._nextTurn(self.turn)


	def _nextTurn(self, turn):

		# sets the next turn
		playerTurns = [False, False]
		playerTurns[turn] = True

		# relays the next turn
		for x in range(2):
			self.players[x].Send({"action": "yourTurn", "torf": playerTurns[x]})
		# self.player0.Send({"action": "yourTurn", "torf": playerTurns[0]})
		# self.player1.Send({"action": "yourTurn", "torf": playerTurns[1]})

		for x in range(3):
			print(self.board[x])



	def roll(self, hasRolled, data, num):
		
		# check if it's user's turn and if they have rolled
		if num == self.turn and not hasRolled:

			# do random from (1 to 4) % 2 == 1 to simulate getting a 0 or a 1
			for x in range(4):
				self.slt_mchn[x] = True if (random.randint(1, 4) % 2) == 1 else False

			move = self.slt_mchn.count(True)

			# update the hasRolled variable
			playerHasRolled = [None, None]
			playerHasRolled[num] = True

			# relay the rolls back to both users and update the relevant 
			# player's hasRolled variable

			for x in range(2):
				self.players[x].Send({"action": "roll", "rolls": self.slt_mchn, "hasRolled": playerHasRolled[x], "num": num})
			# self.player0.Send({"action": "roll", "rolls": self.slt_mchn, "hasRolled": playerHasRolled[0], "num": num})
			# self.player1.Send({"action": "roll", "rolls": self.slt_mchn, "hasRolled": playerHasRolled[1], "num": num})

			# check the valid spaces to allow highlights
			valid = []
			for x in range(14):
				# first case checks normal stone advancements
				# second case checks specifically the rosette case
				# third case checks when placing onto board
				if (x + move < 15 and self.playerpaths[num][x] and # first
					not self.playerpaths[num][x + move] and not x + move == 7 
					or 
					x + move < 15 and self.playerpaths[num][x] and x + move == 7 
					and not (self.playerpaths[0][7] or self.playerpaths[1][7]) 
					or 
					x == move - 1 and not self.playerpaths[num][move - 1] and 
					self.playerscores[num] + self.playerpaths[num].count(True) < NUM_OF_STONES): 
					print(PTOG["m"+ str(x)])
					valid.append(PTOG["m"+str(x)])


			numOfValid = len(valid)
			

					
			if num == 0:
				self.player0.Send({"action": "valid", "moveable": valid})
			else:
				self.player1.Send({"action": "valid", "moveable": valid})


			if numOfValid == 0:
				self.lorTurn("lost", num)




# Start
print("STARTING SERVER ON LOCALHOST")

# address setting
address = input("Host:Port (localhost:8000): ")
if not address:
    host, port = "localhost", 8000
else:
    host, port = address.split(":")

# setting server to address    
Ur_Server = UrServer(localaddr = (host, int(port)))
Ur_Server.launch()