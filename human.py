'''
This class extends the basic player class to implement actions using the GUI
so that a human-controlled player can make moves
'''

import pygame, player, tile

class Human(player.Player):
	
	TRAY_COLOR = (110, 92, 80)
	TRAY_LEFT = 100
	TRAY_TOP = 550
	TRAY_FIRSTLEFT = TRAY_LEFT + tile.Tile.SQUARE_BORDER + tile.Tile.SQUARE_SIZE * .5
	TRAY_FIRSTTOP = TRAY_TOP + tile.Tile.SQUARE_BORDER
	
	'''
	Initialize the human-controlled player (currently does nothing but call's player initialization)
	'''
	def __init__(self, name, theBoard, theBag, theHeuristic = None):
		player.Player.__init__(self, name, theBoard, theBag, 10.0, theHeuristic)
		self.hand = -1
	
	'''
	Try to grab a tile from the tray. If no tile is picked, return None, otherwise return the tile
	grabbed and put the tile in-hand. If there is a tile in-hand, swap it with the tile chosen
	'''
	def pickup(self, x, y):
		index = self.getTrayIndex(x, y)
		
		if index != -1 and index < len(self.tray):
			if self.hand == -1:
				#Pick up the tile
				self.hand = index
				return self.tray[index]
			else:
				#Swap the tiles
				self.tray[index], self.tray[self.hand] = self.tray[self.hand], self.tray[index]

		#if we swapped OR if we tried to pickup something else, dump it		
		self.hand = -1
		return None
		
	'''
	Removes the in-hand piece from the tray
	'''
	def placeTentative(self):		
		if self.hand != -1:
			del self.tray[self.hand]
			self.hand = -1
			
	'''
	Finds the index selected based on screen coordinates provided (returns None if out of range)
	'''
	def getTrayIndex(self, x, y):
		
		x -= Human.TRAY_FIRSTLEFT
		y -= Human.TRAY_FIRSTTOP
		
		#make sure we're in the tile area
		if x >= 0 and y >= 0 and y <= tile.Tile.SQUARE_SIZE:
			#don't count clicks in the gaps between tiles
			if x % (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER) < tile.Tile.SQUARE_SIZE - tile.Tile.SQUARE_BORDER:
				index = (int)(x / (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER))
				#make sure we have tiles that far out
				if index < len(self.tray):
					return index
		return -1
		
	'''
	Draws the tray at the bottom of the screen
	'''	
	def drawTray(self, DISPLAYSURF):
		
		#Draw a basic tray
		pygame.draw.rect(DISPLAYSURF, Human.TRAY_COLOR, (Human.TRAY_LEFT, Human.TRAY_TOP, 
						(tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER)*8, 
						tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER*2))
			
		#Draw each tile
		i = 0
		for t in self.tray:
			top = Human.TRAY_FIRSTTOP
			left = (Human.TRAY_FIRSTLEFT + (i * (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER)))
			
			if i == self.hand:
				highlight = True
			else:
				highlight = False
			
			t.draw(left, top, DISPLAYSURF, highlight)	
			i += 1


	