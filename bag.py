'''
Represents the bag of tiles, contains all tiles which haven't been drawn yet.
Initialized with the exact distribution of tiles, grab() will choose one tile
from the bag at random. If none are available, it will return None
'''

import pygame, random, tile

class Bag:
	
	#sets up the initial distribution of tiles
	def __init__(self):
		self.tiles = []
		
		#Add the initial distribution of tiles
		self.add('A', 1, 9)
		self.add('B', 3, 2)
		self.add('C', 3, 2)
		self.add('D', 2, 4)
		self.add('E', 1, 12)
		self.add('F', 4, 2)
		self.add('G', 2, 3)
		self.add('H', 4, 2)
		self.add('I', 1, 9)
		self.add('J', 8, 1)
		self.add('K', 5, 1)
		self.add('L', 1, 4)
		self.add('M', 3, 2)
		self.add('N', 1, 6)
		self.add('O', 1, 8)
		self.add('P', 3, 2)
		self.add('Q', 10, 1)
		self.add('R', 1, 6)
		self.add('S', 1, 4)
		self.add('T', 1, 6)
		self.add('U', 1, 4)
		self.add('V', 4, 2)
		self.add('W', 4, 2)
		self.add('X', 8, 1)
		self.add('Y', 4, 4)
		self.add('Z', 10, 1)
		self.add(' ', 0, 2)
		
		#DEBUG - Small bag for debugging total game states
		'''self.add('E', 1, 3)
		self.add('S', 1, 3)
		self.add('A', 1, 3)
		self.add('Z', 10, 1)
		self.add('R', 1, 2)
		self.add('I', 1, 2)
		self.add('M', 3, 1)
		self.add('N', 1, 3)'''
		
		random.shuffle(self.tiles)
		
	'''
	Grabs the one tile from the bag and returns it (None if there aren't any left)
	'''
	def grab(self):
		if self.isEmpty():
			return None
		else:
			tile = self.tiles[0]
			self.tiles = self.tiles[1:]
			return tile
			
	def isEmpty(self):
		if len(self.tiles) == 0:
			return True
		return False
		
	def shuffle(self):
		random.shuffle(self.tiles)
		
	def putBack(self, tile):
		self.tiles.append(tile)
		
	'''
	Adds the tile n times into the bag
	'''	
	def add(self, letter, points, n):
		for i in range(n):
			self.tiles.append(tile.Tile(letter, points))
		