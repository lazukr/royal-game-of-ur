import pygame
import math
import random
from collections import namedtuple

# general constants
GRID_SIZE = 45
NUM_OF_PLAYERS = 2
STARTING_STONES = 7
FONT_SIZE = 32
TICKRATE = 60

class Size(namedtuple('Size', ['width', 'height'])):
    def __new__(cls, width=GRID_SIZE, height=GRID_SIZE):
        return super(Size, cls).__new__(cls, width, height)

class Position(namedtuple('Position', ['x', 'y'])):
    def __new__(cls, x=0, y=0):
        return super(Position, cls).__new__(cls, x, y)

    def add(self, position):
        return Position(self.x + position.x, self.y + position.y)

    def times(self, value):
        return Position(self.x * value, self.y * value)

class Highlighter(namedtuple('Highlighter', ['cursor', 'darken', 'valid', 'invalid'])):
    def __new__(cls, cursor=0, darken=0, valid=0, invalid=0):
        return super(Highlighter, cls).__new__(cls, cursor, darken, valid, invalid)

    def set(cursor=0, darken=0, valid=0, invalid=0):
        self.cursor = cursor
        self.darken = darken
        self.valid = valid
        self.invalid = invalid

    def add(self, highlighter):
        new_cursor = self.cursor | highlighter.cursor
        new_darken = self.darken | highlighter.darken
        new_valid = self.valid | highlighter.valid
        new_invalid = self.invalid | highlighter.invalid
        return Highlighter(new_cursor, new_darken, new_valid, new_invalid)

    def remove(self, highlighter):
        new_cursor = self.cursor & (~highlighter.cursor)
        new_darken = self.darken & (~highlighter.darken)
        new_valid = self.valid & (~highlighter.valid)
        new_invalid = self.invalid & (~highlighter.invalid)
        return Highlighter(new_cursor, new_darken, new_valid, new_invalid)

# colours
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
BLUE = pygame.Color(0, 0, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)
BG_ORANGE = pygame.Color(198, 106, 17)

# highlights
VALID_HIGHLIGHT = pygame.Color(0, 255, 0, 100) # Green @ alpha = 100
INVALID_HIGHLIGHT = pygame.Color(255, 0, 0, 100) # Red @ alpha = 100
CURSOR_HIGHLIGHT = pygame.Color(255, 255, 0, 100) # Yellow @ alpha = 100
DARKEN_HIGHLIGHT = pygame.Color(0, 0, 0, 100) # Black @ alpha = 100

CURSOR = Highlighter(1, 0, 0, 0)
DARKEN = Highlighter(0, 1, 0, 0)
VALID = Highlighter(0, 0, 1, 0)
INVALID = Highlighter(0, 0, 0, 1)

# coordinate constants
SQUARE = Size()
BOARD_GRID = Size(8, 3)
WINDOW_SIZE = Size(12*GRID_SIZE, 11*GRID_SIZE)
BOARD_POSITION = Position(5, 3*GRID_SIZE)

# text
CAPTION = "Royal Game of Ur"

# images
BOARD_IMAGE = pygame.image.load("assets/Board.png")
WHITE_STONE = pygame.image.load("assets/White_Stone.png")
BLACK_STONE = pygame.image.load("assets/Black_Stone.png")

class Display:
    def __init__(self, image, position):
        self.image = image
        self.position = position

    @classmethod
    def getRect(cls, size, colour, position):
        surface = pygame.Surface(size)
        surface.fill(colour)
        surface.set_alpha(colour.a)
        return cls(surface, position)

class DisplayList:
    def __init__(self):
        self.display_list = []

    def add(self, display):
        self.display_list.append(display)

    def clear(self):
        self.display_list = []

    def __iter__(self):
        for x in range(len(self.display_list)):
            yield self.display_list[x]

class Player:
    def __init__(self, colour, stones):
        self.colour = colour
        self.stones = stones
        self.score = 0

class Tile(DisplayList):
    def __init__(self, position):
        super(Tile, self).__init__()
        self.position = position
        self.highlighter = Highlighter()
        self._init_highlights()

    def _init_highlights(self):
        self.highlight_valid = Display.getRect(SQUARE, VALID_HIGHLIGHT, self.position)
        self.highlight_invalid = Display.getRect(SQUARE, INVALID_HIGHLIGHT, self.position)
        self.highlight_cursor = Display.getRect(SQUARE, CURSOR_HIGHLIGHT, self.position)
        self.highlight_darken = Display.getRect(SQUARE, DARKEN_HIGHLIGHT, self.position)

    def set_highlight(self, highlighter):
        self.highlighter = self.highlighter.add(highlighter)
        self._update()

    def _update(self):
        self.clear()
        if (self.highlighter.cursor):
            self.add(self.highlight_cursor)

        if (self.highlighter.darken):
            self.add(self.highlight_darken)

        if (self.highlighter.valid):
            self.add(self.highlight_valid)

        if (self.highlighter.invalid):
            self.add(self.highlight_invalid)


class Board:
    def __init__(self, image, position, grid):
        self.position = position
        self.display = Display(image, position)
        self.grid = grid
        self._init_board()

    def _init_board(self):
        self.board = list([] for x in range(self.grid.width))
        for x in range(self.grid.width):
            self.board[x] = list([] for y in range(self.grid.height))
            for y in range(self.grid.height):
                tile_position = Position(x, y).times(GRID_SIZE).add(self.position)
                self.board[x][y] = Tile(tile_position)

    def __iter__(self):
        yield self.display
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                yield self.board[x][y]

class View:
    def __init__(self, window_size, background_colour):
        self.window_size = window_size
        self.background_colour = background_colour
        self.display = Display.getRect(self.window_size, self.background_colour, Position(0, 0))
        self._init_pygame()

    def _init_pygame(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(self.window_size)
        self.caption = pygame.display.set_caption(CAPTION)

    def render(self, display):
        try:
            iterator = iter(display)
        except TypeError:
            self.screen.blit(display.image, display.position)
        else:
            for element in display:
                self.render(element)

    def update(self):
        pygame.display.flip()

class Game:
    def __init__(self, size, background_colour, tickrate):
        self.size = size
        self.background_colour = background_colour
        self.tickrate = tickrate
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.view = View(self.size, self.background_colour)
        self.board = Board(BOARD_IMAGE, BOARD_POSITION, BOARD_GRID)

    def _draw(self):
        self.view.render(self.view.display)
        self.view.render(self.board)
        self.view.update()

    def update(self):
        self.clock.tick(self.tickrate)
        self._draw()


if __name__ == "__main__":
    game = Game(WINDOW_SIZE, WHITE, TICKRATE)
    while 1:
        game.update()
