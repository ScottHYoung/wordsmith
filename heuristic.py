'''
This file contains various heuristic classes all meant to adjust the
word choice for the AI in various ways, such as from tiles selected to
the board positions
'''

import board, player, tile, aistats

# BASE CLASS
class Heuristic(object):
	
	def __init__(self):
		self.stats = aistats.AIStats()
	
	'''
	Given various data about the move being played, this determines gives an
	adjustment number in terms of points for how the play should be revalued
	'''
	def adjust(self, trayTiles = None, seedRatio = None, playTiles = None):
		return 0
		
#===================================================
#			HEURISTIC CLASSES
#===================================================
'''
	--Tile Quantile Heuristic--
	
	The motivation behind this heuristic is that some letters are
	more useful than others. Useful letters should be given a penalty,
	so that their value isn't wasted on low-scoring words. Similarly,
	unuseful letters should be encouraged to be discarded at higher
	rates since they represent a liability in the tray.
	
	The way this heuristic works is that it uses letterPlay data 
	previously collected to determine the quantile difference (defaults to .5 mass)
	between the play for all letters is at that quantile, versus the
	value of that particular letter.
	
	The adjustment is then the sum of all quantile differences multiplied
	by the weight of the heuristic (again, defaulting to .5)
	
	What the algorithm means:
		-Low quantiles means a more conservative adjustment (accepting a lot of luck)
		-High quantiles means a more aggressive adjustment (hoping to get lucky)
		-The weight impacts the strength of this heuristic relative to the raw score
		 and/or other heuristics
	
'''
class tileQuantileHeuristic(Heuristic):
	
	def __init__(self, quantile = .5, weight = .5):
		Heuristic.__init__(self)
		
		allLetters = self.stats.letterPlaysInvCDF(None, quantile)
		
		self.totalAdjustment = 0
		self.adjustmentsMade = 0
		
		self.letterAdjust = {}
		for code in range(ord('A'), ord('Z')+1):
			char = chr(code)
			self.letterAdjust[char] = (allLetters - self.stats.letterPlaysInvCDF(char, quantile)) * weight
		char = '_'
		self.letterAdjust[char] = (allLetters - self.stats.letterPlaysInvCDF(char, quantile)) * weight
			
	def adjust(self, trayTiles = None, seedRatio = None, playTiles = None):
		adjustment = super(tileQuantileHeuristic, self).adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		
		if playTiles != None:
			for pos, tile in playTiles:
				if tile.isBlank:
					letter = '_'
				else:
					letter = tile.letter
				adjustment += self.letterAdjust[letter]
			
		return adjustment
		seedRatio = None

'''
This takes another heuristic as an initializing parameter and applies its effect ONLY if
we're not in an end-game situation. This prevents the dynamic strategy from being aggressive
when at the end of the game and it no longer makes sense to play conservatively
'''		
class notEndGameHeuristic(Heuristic):
	
	def __init__(self, h):
		Heuristic.__init__(self)
		self.heuristic = h
	
	def adjust(self, trayTiles = None, seedRatio = None, playTiles = None):
		adjustment = super(notEndGameHeuristic, self).adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		if len(trayTiles) == player.Player.TRAY_SIZE:
			adjustment += self.heuristic.adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		return adjustment
			
'''
This is the opposite of notEndGame, applying the heuristic ONLY when we have limited tiles
'''		
class endGameHeuristic(Heuristic):

	def __init__(self, h):
		Heuristic.__init__(self)
		self.heuristic = h

	def adjust(self, trayTiles = None, seedRatio = None, playTiles = None):
		adjustment = super(endGameHeuristic, self).adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		if not len(trayTiles == player.Player.TRAY_SIZE):
			adjustment += self.heuristic.adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)	
		return adjustment		
			
'''
This allows for multiple heuristics to be applied simultaneously, iterating through each
and summing their values
'''			
class multiHeuristic(Heuristic):
	
	def __init__(self, listOfHeuristics):
		Heuristic.__init__(self)
		
		self.heuristics = listOfHeuristics
		
	def adjust(self, trayTiles = None, seedRatio = None, playTiles = None):
		adjustment = super(multiHeuristic, self).adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		
		for h in self.heuristics:
			adjustment += h.adjust(trayTiles = trayTiles, seedRatio = seedRatio, playTiles = playTiles)
		
		return adjustment