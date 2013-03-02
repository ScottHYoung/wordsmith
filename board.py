import pygame, tile, player, dictionarywords, wordfrequency, time
from pygame.locals import *

class Board:
	
	DEBUG_ERRORS = True
	
	NORMAL = 'normal'
	DOUBLEWORD = 'doubleword'
	TRIPLEWORD = 'tripleword'
	DOUBLELETTER = 'doubleletter'
	TRIPLELETTER = 'tripleletter'
	
	DICTIONARY_FILE = 'media/scrabblewords_usage.txt'
	
	GRID_SIZE = 15 			#size in # of squares
	START_POSITION = (7, 7)
	SQUARE_SIZE = tile.Tile.SQUARE_SIZE
	SQUARE_BORDER = tile.Tile.SQUARE_BORDER
	BOARD_TOP = 0
	BOARD_LEFT = 0
	
	#Prompt Details
	PROMPT_LEFT = 145
	PROMPT_TOP = 200
	PROMPT_WIDTH = 250
	PROMPT_HEIGHT = 75
	PROMPT_FONT = None
	
	
	
	BEIGE = (200, 180, 165)
	RED	= (200, 0, 0)
	BLUE = (0, 0, 200)
	PINK = (255, 100, 100)
	LBLUE = (100, 100, 255)
	
	MASK_COLOR = (0, 0, 0, 100)
	
	'''
	Initialize the board, create the squares matrix and mark all the special
	squares
	'''
	def __init__(self):
		
		self.squares = []
		for x in range(Board.GRID_SIZE):
			self.squares.append([])
			for y in range(Board.GRID_SIZE):
				#squares are a tuple of a tile and a square bonus
				self.squares[x].append((None, Board.NORMAL))
		
		#------------BONUS SQUARES------------------		
		triplewords = [(0,0), (7,0), (14,0), (0,7), (14,7), (0,14), (7,14), (14,14)]	
		for (x, y) in triplewords:
			self.squares[x][y] = (None, Board.TRIPLEWORD)
		
		doublewords = [(1,1), (2,2), (3,3), (4,4), (1,13), (2,12), (3,11), (4,10),
					   (13,1), (12,2), (11,3), (10,4), (13,13), (12,12), (11,11), (10,10),
					   (7,7)]
		for (x, y) in doublewords:
			self.squares[x][y] = (None, Board.DOUBLEWORD)
			
		tripleletters = [(5,1), (9,1), (1,5), (1,9), (5,13), (9,13), (13,5), (13,9),
						 (5,5), (9,9), (5,9), (9,5)]
		for (x, y) in tripleletters:
			self.squares[x][y] = (None, Board.TRIPLELETTER)
		
		doubleletters = [(3,0), (0,3), (11,0), (0,11), (3,14), (11,14), (14,3), (14,11),
						 (2,6), (3,7), (2,8), (6,2), (7,3), (8,2), (6,12), (7,11), (8,12),
						 (12,6), (11,7), (12,8), (6,6), (8,8), (6,8), (8,6)]
		for (x, y) in doubleletters:
			self.squares[x][y] = (None, Board.DOUBLELETTER)
		#-----------------------------------------
		
		#These locks control which row/column can be played upon (so players must play in a straight line)
		self.columnLock = -1
		self.rowLock = -1
		
		#Load the dictionary
		self.dictionary = dictionarywords.DictionaryWords(Board.DICTIONARY_FILE)
		
		#Load the file keeping track of word usage
		self.wordfreq = wordfrequency.WordFrequency()
		
		#Reset all timers
		self.resetAllMetrics()
		
		#load font
		Board.PROMPT_FONT = pygame.font.Font('freesansbold.ttf', 20)
		
	
	'''
	Locates a board position and tries to put a tile there, returns False if the
	square is occupied, the position is outside the bounds of the board, or if
	play has already been constrained in a particular direction
	'''		
	def placeTentative(self, x, y, tile):
		(boardX, boardY) = self.getBoardPosition(x, y)
		
		if self.checkLocks(boardX, boardY):
			if boardX >= 0 and boardY >= 0 and boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
				previousTile = self.squares[boardX][boardY][0]
				if previousTile == None:
					self.squares[boardX][boardY] = (tile, self.squares[boardX][boardY][1])
					if tile.isBlank:
						return ("ASK", tile)
					self.setLocks()
					return (True, tile)
		return (False, tile)
		
	'''
	Returns true if the position is playable based on the lock combinations
	'''
	def checkLocks(self, boardX, boardY):
		if (self.rowLock >= 0 and self.columnLock >= 0) and (boardX == self.columnLock or boardY == self.rowLock):
			locksOkay = True
		elif self.columnLock >= 0 and boardX == self.columnLock:
			locksOkay = True
		elif self.rowLock >= 0 and boardY == self.rowLock:
			locksOkay = True
		elif self.rowLock < 0 and self.columnLock < 0:
			locksOkay = True
		else:
			locksOkay = False
		return locksOkay		
		
	'''
	This scans the board. If there is one unlocked piece, set both a row/col lock. If there are two
	set only the lock for that col, row. If there are none, remove all locks
	'''	
	def setLocks(self):
		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append((x, y))
		#Case 1: No tentative tiles
		if len(inPlay) == 0:
			self.columnLock = -1
			self.rowLock = -1
		#Case 2: One tentative tile, allow play on row and col
		elif len(inPlay) == 1:
			self.columnLock = inPlay[0][0]
			self.rowLock = inPlay[0][1]
		#Case 3: More than one tentative tile, disable play outside of line
		else:	
			col = inPlay[0][0]
			row = inPlay[0][1]
			inACol = True
			inARow = True
			for t in inPlay:
				if(t[0] != col):
					inACol = False
				if(t[1] != row):
					inARow = False
			
			#we shouldn't be able to place tentative tiles outside a line
			assert inARow or inACol and not(inARow and inACol)
			
			if inACol:
				self.columnLock = col
				self.rowLock = -1
			elif inARow:
				self.columnLock = -1
				self.rowLock = row	
					
	
	'''
	Attempts to remove the tile from the given square, returns the tile if it
	was removed successfully, otherwise returns None if the pointer was out of range,
	the square didn't have a tile or if the tile was locked
	'''	
	def remove(self, x, y):
		(boardX, boardY) = self.getBoardPosition(x, y)	
		if boardX >= 0 and boardY >= 0 and boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
			tile = self.squares[boardX][boardY][0]
			if tile != None and not tile.locked:
				self.squares[boardX][boardY] = (None, self.squares[boardX][boardY][1])
				self.setLocks()
				return tile
		return None
			
	'''
	Returns the (boardX, boardY) tuple of the coordinates on the board based on screen coords
	'''
	def getBoardPosition(self, x, y):
		x -= Board.BOARD_LEFT + Board.SQUARE_BORDER
		y -= Board.BOARD_TOP + Board.SQUARE_BORDER
		
		#make sure we're in the tile area
		if x >= 0 and y >= 0:
			#don't count clicks in the gaps between tiles
			if (x % (Board.SQUARE_SIZE + Board.SQUARE_BORDER) < Board.SQUARE_SIZE - Board.SQUARE_BORDER and
			   y % (Board.SQUARE_SIZE + Board.SQUARE_BORDER) < Board.SQUARE_SIZE - Board.SQUARE_BORDER):
				boardX = (int)(x / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))
				boardY = (int)(y / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))
				#make sure we haven't gone off the board
				if boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
					return (boardX, boardY)
		return (-1, -1)
		
	
	'''
	Puts a tile on the board (board, not screen coords, for that use placeTentative)
	'''	
	def setPiece(self, (x,y), tile):
		assert x >= 0 and y >= 0 and x < Board.GRID_SIZE and y < Board.GRID_SIZE
		assert self.squares[x][y][0] == None
		self.squares[x][y] = (tile, self.squares[x][y][1])
		
	'''
	This function works by going through all tentative tiles on the board, validating the move
	and then processing the play. The return value is a tuple of (tiles, points) with the former
	being returned tiles in a move failure and the latter being the score in the case of success.
	
	In success, the tiles are locked, in failure, the tiles are removed entirely.
	
	Validation Rules:
	
		1) At least one tile must be tentative
		2) All tentative tiles must lie on one line
		3) On the first turn, one tile must be located on square START_POSITION
		4) Linear word must be unbroken (including locked tiles)
		5) On every other turn, at least one crossword must be formed
		6) All words formed must be inside the dictionary
	
	'''	
	def play(self, isFirstTurn=True):

		
		#collect all tentative tiles
		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append((x, y))
		
		#VALIDATION STEP ONE: There must be at least one tile played
		if len(inPlay) <= 0:
			#fail
			if Board.DEBUG_ERRORS:
				print "Play requires at least one tile."
			return ([], -1)			
			
		#VALIDATION STEP TWO: Tiles must be played on a straight line			
		col = inPlay[0][0]
		row = inPlay[0][1]
		inACol = True
		inARow = True
		for (x,y) in inPlay:
			if(x != col):
				inACol = False
			if(y != row):
				inARow = False
		
		if not inARow and not inACol:
			#fail, remove tiles and return	
			if Board.DEBUG_ERRORS:
				print "All tiles must be placed along a line."		
			return (self.removeTempTiles(), -1)
		
		#VALIDATION STEP THREE: If isFirstTurn, then one tile must be on START_POSITION
		if not Board.START_POSITION in inPlay and isFirstTurn:
			return(self.removeTempTiles(), -1)
		
		#VALIDATION STEP FOUR: Word created is unbroken
		unbroken = True
		left = col
		right = col
		top = row
		bottom = row
		
		#Determine the span of the word in either up/down or left/right directions
		for (x, y) in inPlay:
			if x < left:
				left = x
			elif x > right:
				right = x
			if y < top:
				top = y
			elif y > bottom:
				bottom = y
				
		#Confirm that the span is unbroken
		if inACol:
			for y in range(top, bottom+1):
				if self.squares[col][y][0] == None:
					unbroken = False
		elif inARow:
			for x in range(left, right+1):
				if self.squares[x][row][0] == None:
					unbroken = False
					
		if not unbroken:
			return(self.removeTempTiles(), -1)			
			
		
		#VALIDATION STEPS FIVE & SIX:
		(totalScore, spellings, seedRatio) = self.validateWords(isFirstTurn, inPlay=inPlay)
		
		if spellings != None:
			for spelling in spellings:
				self.wordfreq.wordPlayed(spelling)
				
			self.wordfreq.save()
		
		if totalScore < 0:
			return(self.removeTempTiles(), -1)
			

		#Lock tiles played
		for (x,y) in inPlay:
			self.squares[x][y][0].locked = True			
			
		#Remove the locks on the board
		self.columnLock = -1
		self.rowLock = -1	
			
		return (None, totalScore)
		
	'''
	Recursively searches through the conflicted word space, trying all permutations
	to see which assignment of word score bonuses yields the highest points
	'''
	def wordScoreTreeSearch(self, conflicts, scores, bonusesApplied = []):
		#BASE CASE: count up scores + bonuses return value
		if len(conflicts) == 0:
			totalScore = 0
			for (bonus, word) in bonusesApplied:
				totalScore += scores[word] * bonus
				return (totalScore, bonusesApplied)
		#RECURSIVE CASE: conflicts remain, so recursively check both possible bonus applications
		else:
			#apply bonus to first crossword
			bonusesApplied1 = bonusesApplied[:]
			bonusesApplied1.append((conflicts[0][0], conflicts[0][1][0]))
			score1 = self.wordScoreTreeSearch(conflicts[1:], scores, bonusesApplied1)
			
			#apply bonus to second crossword
			bonusesApplied2 = bonusesApplied[:]
			bonusesApplied2.append((conflicts[0][0], conflicts[0][1][1]))
			score2 = self.wordScoreTreeSearch(conflicts[1:], scores, bonusesApplied2)
			
			if score1 > score2:
				bestScore = score1
				bestBonusCombos = bonusesApplied1
			else:
				bestScore = score2
				bestBonusCombos = bonusesApplied2
			
			return (bestScore, bestBonusCombos)
		
	'''
	Checks if all the words played are valid and calculates the score, used for two purposes
		1) as the second half of the play() algorithm
		2) independently for AI verification checks
	'''
	def validateWords(self, isFirstTurn, tilesPlayed=None, inPlay=None, vocabulary=-1):
		if Board.DEBUG_ERRORS:
			startTime = time.time()
		
		wordsBuilt = [] #a list containing lists of ((x, y), tile)
	
		#If we're doing this step separately from normal play, put the tiles on to run
		#the algorithm
		if tilesPlayed != None:
			inPlay = []
			for pos, tile in tilesPlayed:
				self.setPiece(pos,tile)
				inPlay.append(pos)
					
		if Board.DEBUG_ERRORS:
			crosswordTimeStart = time.time()
			self.quickValidationTime += crosswordTimeStart - startTime			
			
		#Calculate the seed ratio to return to for heuristics
		seedRatio = self.calculateSeedRatio()		
		
	
		#VALIDATION STEP FIVE: Ensure a crossword is formed (also keep a list of 'words built')	
		'''
		Algorithm description: We can find all the crosswords by going through all the rows
		and columns which contain tentative tiles. These are potential 'words'. Then we start
		with a tentative tile on that row/col and expand outward in both directions until we
		hit a blank on both ends. That becomes the 'word' created. Finally, we go through the
		words and confirm that a previously played tile was used
		'''
	
		#First build a list of possible word rows and cols (include x and y for the first seed tile)
		rowsToCheck = []
		colsToCheck = []
		colsSet = []
		rowsSet = []
		for (x, y) in inPlay:
			if not x in colsSet:
				colsSet.append(x)
				colsToCheck.append((x, y))
			if not y in rowsSet:
				rowsSet.append(y)
				rowsToCheck.append((x, y))
		
		#Build words along rows
		for (col, row) in rowsToCheck:
			
			#build left
			left = col
			while left-1 >= 0 and self.squares[left-1][row][0] != None:	
				left -= 1
			
			#build right
			right = col
			while right+1 < Board.GRID_SIZE and self.squares[right+1][row][0] != None:
				right += 1
			
			#Add the word built if it has at least 2 letters
			if left != right:
				wordsBuilt.append([((x,row), self.squares[x][row][0]) for x in range(left, right+1)])

		#Build words along cols
		for (col, row) in colsToCheck:

			#build up
			up = row
			while up-1 >= 0 and self.squares[col][up-1][0] != None:	
				up -= 1

			#build down
			down = row
			while down+1 < Board.GRID_SIZE and self.squares[col][down+1][0] != None:
				down += 1

			#Add the word built
			if up != down:
				wordsBuilt.append([((col,y), self.squares[col][y][0]) for y in range(up, down+1)])
				
		crosswordMade = False	
		for word in wordsBuilt:
			for ((x,y), tile) in word:
				if tile.locked:
					crosswordMade = True	
					
		if Board.DEBUG_ERRORS:
			validationTimeStart = time.time()
			self.crosswordValidationTime += time.time() - crosswordTimeStart					
					
		if not crosswordMade and not isFirstTurn:
			#fail, word is unattached
			if Board.DEBUG_ERRORS:
				self.crosswordErrors += 1
				if tilesPlayed == None:
					print "Word placed must form at least one crossword."
			self.pullTilesFast(tilesPlayed)			
			return (-1, None, seedRatio)		
					
			
		#TO-DO
		#VALIDATION STEP SIX: Ensure all words in wordsBuilt are in the Scrabble Dictionary
		spellings = []
		for word in wordsBuilt:
			spelling = ""
			for (pos, tile) in word:
				spelling += tile.letter
			spellings.append(spelling)	
			if not self.dictionary.isValid(spelling, vocabulary):
				#fail, word isn't a valid scrabble word
				if Board.DEBUG_ERRORS:
					self.invalidWordCount += 1
					if tilesPlayed == None:
						print "'"+spelling+"' isn't in the dictionary."
				self.pullTilesFast(tilesPlayed)				
				return (-1, None, seedRatio)
		
		if Board.DEBUG_ERRORS:
			scoringTimeStart = time.time()
			self.dictionaryValidationTime += time.time() - validationTimeStart		
		
		#Calculate score
		totalScore = 0
		
		#50 point bonus for using all tiles
		if len(inPlay) == player.Player.TRAY_SIZE:
			totalScore += 50
		
		wordScores = {}	#contains word - points references for each word
		wordScoreOptimize = []	#stores words where word bonuses are conflicted	
		i=0
		marks = []		#We can only get bonuses for one word, so only apply corner bonuses once
		for word in wordsBuilt:
			wordScores[i] = 0
			wordBonus = 1
			for (x, y), tile in word:
				letterScore = tile.points
				if self.squares[x][y][0].locked == False: #Can't get bonuses for previously played tiles
					crosswords = self.shared((x,y), wordsBuilt)
					bonus = self.squares[x][y][1]
					if bonus == Board.DOUBLELETTER and not (x,y) in marks:
						letterScore *= 2
						marks.append((x,y))
					elif bonus == Board.TRIPLELETTER and not (x,y) in marks:
						letterScore *= 3
						marks.append((x,y))
					elif bonus == Board.DOUBLEWORD:
						if len(crosswords) <= 1:
							wordBonus *= 2
						else:
							if not (2, crosswords) in wordScoreOptimize:
								wordScoreOptimize.append((2, crosswords))
					elif bonus == Board.TRIPLEWORD:
						if len(crosswords) <= 1:
							wordBonus *= 3
						else:
							if not (3, crosswords) in wordScoreOptimize:
								wordScoreOptimize.append((3, crosswords))
				wordScores[i] += letterScore
			wordScores[i] *= wordBonus
			i+=1
			
		#If are conflicts, then go through all permutations to retrieve the highest possible score		
		if len(wordScoreOptimize) > 0:
			(best, bestWordScores) = self.wordScoreTreeSearch(wordScoreOptimize, wordScores)
			for (bonus, word) in bestWordScores:
				wordScores[word] *= bonus	
		
		#Now add up all the words to make the total score		
		for score in wordScores.values():
			totalScore += score	
			
		if Board.DEBUG_ERRORS:
			self.scoringTime += time.time() - scoringTimeStart			
			
		#Pull the tiles (faster than removeTempTiles) if we put them on in this call
		self.pullTilesFast(tilesPlayed)
				
		return (totalScore, spellings, seedRatio)
	
	'''
	Resets all timers
	'''
	def resetAllMetrics(self):
		self.scoringTime = 0
		self.crosswordValidationTime = 0
		self.dictionaryValidationTime = 0
		self.quickValidationTime = 0
		self.invalidWordCount = 0
		self.crosswordErrors = 0
	
	'''
	Removes tiles if we already know where they are
	'''			
	def pullTilesFast(self, tilesPlayed):
		if tilesPlayed != None:
			for (x,y), tile in tilesPlayed:
				assert self.squares[x][y][0] != None
				assert self.squares[x][y][0].locked == False
				if self.squares[x][y][0].isBlank:
					self.squares[x][y][0].letter = ' '
				self.squares[x][y] = (None, self.squares[x][y][1])
					
	'''
	Returns a list of all word indices using the given tile
	'''	
	def shared(self, pos, words):
		wordsUsingPos = []
		i = 0
		for word in words:
			for (coords, tile) in word:
				if pos == coords:
					wordsUsingPos.append(i)
			i+=1
					
		return wordsUsingPos
			
	'''
	Removes the temporary tiles on the board and returns them as a list
	'''
	def removeTempTiles(self):
		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append(self.squares[x][y][0])
					self.squares[x][y] = (None, self.squares[x][y][1])
		
		#Remove the locks the player can play again
		self.columnLock = -1
		self.rowLock = -1
		
		return inPlay
		
	'''
	Calculates the number of seeds and number of tiles and returns them as a tuple
	'''
	def calculateSeedRatio(self):
		numSeeds = 0
		numTiles = 0
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None:
					numTiles += 1
				elif ((x > 0 and self.squares[x-1][y][0] != None) or
					  (x < Board.GRID_SIZE-1 and self.squares[x+1][y][0] != None) or
					  (y > 0 and self.squares[x][y-1][0] != None) or
					  (y < Board.GRID_SIZE-1 and self.squares[x][y+1][0] != None)):
					numSeeds += 1
				
		
		#If the board is empty, then there is one seed		
		if numSeeds == 0:
			numSeeds = 1
			
		return (numSeeds, numTiles)
		
	'''
	Prompts player to set a letter for the blank character
	'''	
	def askForLetter(self, blank, DISPLAYSURF, ALPHASURF):
		assert blank.isBlank
		
		letter = None
		self.drawLetterPrompt(DISPLAYSURF, ALPHASURF)
		while letter == None:
			for event in pygame.event.get():
				if event.type == KEYUP:
					if event.key == K_a:
						letter = 'A'
					elif event.key == K_b:
						letter = 'B'
					elif event.key == K_c:
						letter = 'C'
					elif event.key == K_d:
						letter = 'D'
					elif event.key == K_e:
						letter = 'E'
					elif event.key == K_f:
						letter = 'F'
					elif event.key == K_g:
						letter = 'G'
					elif event.key == K_h:
						letter = 'H'
					elif event.key == K_i:
						letter = 'I'
					elif event.key == K_j:
						letter = 'J'
					elif event.key == K_k:
						letter = 'K'
					elif event.key == K_l:
						letter = 'L'
					elif event.key == K_m:
						letter = 'M'
					elif event.key == K_n:
						letter = 'N'
					elif event.key == K_o:
						letter = 'O'
					elif event.key == K_p:
						letter = 'P'
					elif event.key == K_q:
						letter = 'Q'
					elif event.key == K_r:
						letter = 'R'
					elif event.key == K_s:
						letter = 'S'
					elif event.key == K_t:
						letter = 'T'
					elif event.key == K_u:
						letter = 'U'
					elif event.key == K_v:
						letter = 'V'
					elif event.key == K_w:
						letter = 'W'
					elif event.key == K_x:
						letter = 'X'
					elif event.key == K_y:
						letter = 'Y'
					elif event.key == K_z:
						letter = 'Z'
			pygame.display.update()
		
		#Now set the letter
		blank.letter = letter

	'''
	Draws a letter prompt to ask for the blank letter
	'''												
	def drawLetterPrompt(self, DISPLAYSURF, ALPHASURF):
		
		#Draw prompt shadow
		ALPHASURF.fill((0,0,0,0))
		pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (Board.PROMPT_LEFT, Board.PROMPT_TOP, Board.PROMPT_WIDTH+4, Board.PROMPT_HEIGHT+4))
		
		#Draw prompt box	
		pygame.draw.rect(ALPHASURF, (0,0,0,200), (Board.PROMPT_LEFT-1, Board.PROMPT_TOP-1, Board.PROMPT_WIDTH+2, Board.PROMPT_HEIGHT+2))
		pygame.draw.rect(ALPHASURF, (255, 255, 255, 200), (Board.PROMPT_LEFT, Board.PROMPT_TOP, Board.PROMPT_WIDTH, Board.PROMPT_HEIGHT))
		
		DISPLAYSURF.blit(ALPHASURF, (0,0))
		
		#Draw text
		promptText = Board.PROMPT_FONT.render("TYPE A LETTER A-Z", True, (0,0,0,200), (255,255,255,200))
		promptRect = promptText.get_rect()
		promptRect.center = (Board.PROMPT_LEFT+Board.PROMPT_WIDTH/2, Board.PROMPT_TOP+Board.PROMPT_HEIGHT/2)
		DISPLAYSURF.blit(promptText, promptRect)
		
	'''
	Redraws only tiles which are animating
	'''	
	def drawDirty(self, DISPLAYSURF, ALPHASURF):
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				#draw position
				(tile, bonus) = self.squares[x][y]
				if tile != None:
					left = x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_LEFT
					top = y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_TOP
					tile.drawDirty(left, top, DISPLAYSURF, (not tile.locked))
																																				
			
	'''
	Draw the board and any placed tiles
	'''			
	def draw(self, DISPLAYSURF, ALPHASURF):
		
		#draw each square
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				#draw position
				left = x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_LEFT
				top = y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_TOP
					
				(tile, bonus) = self.squares[x][y]
				if(bonus == Board.NORMAL):
					color = Board.BEIGE
				elif(bonus == Board.DOUBLEWORD):
					color = Board.PINK
				elif(bonus == Board.TRIPLEWORD):
					color = Board.RED
				elif(bonus == Board.DOUBLELETTER):
					color = Board.LBLUE
				elif(bonus == Board.TRIPLELETTER):
					color = Board.BLUE
				else:
					assert(False)
				pygame.draw.rect(DISPLAYSURF, color, (left, top, Board.SQUARE_SIZE, Board.SQUARE_SIZE))
				
				if(tile != None):
					if tile.locked:
						highlight = False
					else:
						highlight = True
					tile.draw(left, top, DISPLAYSURF, highlight)
		
		#=======DRAW LOCK SHADING==========
		ALPHASURF.fill((0,0,0,0))
		top = Board.BOARD_TOP
		left = Board.BOARD_LEFT
		right = Board.GRID_SIZE*(Board.SQUARE_BORDER + Board.SQUARE_SIZE) + Board.SQUARE_BORDER
		bottom = Board.GRID_SIZE*(Board.SQUARE_BORDER + Board.SQUARE_SIZE) + Board.SQUARE_BORDER
		x1 = self.columnLock * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.BOARD_LEFT
		x2 = x1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER
		y1 = self.rowLock * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.BOARD_LEFT
		y2 = y1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER				
		if self.rowLock >= 0 and self.columnLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, x1-left, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, y2, x1-left, bottom-y2))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, top, right-x2, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, y2, right-x2, bottom-y2))
		elif self.rowLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, right-left, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, y2, right-left, bottom-y2))
		elif self.columnLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, x1-left, bottom-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, top, right-x2, bottom-top))
			
		DISPLAYSURF.blit(ALPHASURF, (0,0))
		#=================================
			