'''
This class creates a player which automatically plays (NOTE: the meat of this class
is actually located in the superclass, Player. This was moved so that human players
can get "hints")
'''
import pygame, player, board, bag
from pygame.locals import *

class AI(player.Player):
	
	
	'''
	Initializes the AI
	'''
	def __init__(self, theBoard, theBag, theDifficulty = 10, theHeuristic = None):
		player.Player.__init__(self, "Wordsmith", theBoard, theBag, theDifficulty, theHeuristic)
	

		