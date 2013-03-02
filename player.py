'''
Generic player object, can be inherited by Human or AI classes which
execute the actions of the player by either GUI interaction or algorithm
'''

import pygame, time
import board, tile, bag, aistats, heuristic
from pygame.locals import *

class Player:
	
	PROGRESS_TOP = 220
	PROGRESS_LEFT = 570
	PROGRESS_WIDTH = 140
	PROGRESS_HEIGHT = 7
	PROGRESS_MARGIN = 25
	
	PROGRESS_COLOR_BACK = (200, 200, 255)
	PROGRESS_COLOR_FRONT = (100, 100, 255)
	
	FONT_COLOR = (55, 46, 40)
	BACKGROUND_COLOR = (255, 255, 255)
	
	TIMEOUT = 15	
	
	TRAY_SIZE = 7
	
	initialized = False
	
	@staticmethod
	def initialize():
		Player.FONT = pygame.font.Font('freesansbold.ttf', 18)
		Player.initialized = True
		Player.aiStats = aistats.AIStats()	
	
	
	'''
	Initialize a new player with a tray and score
	'''
	def __init__(self, name, theBoard, theBag, theDifficulty = 10.0, theHeuristic = None):
		if not Player.initialized:
			Player.initialize()
		
		self.tray = []
		self.score = 0
		self.name = name
		self.theBoard = theBoard
		self.theBag = theBag
		self.lastScorePulse = 0
		self.lastScore = 0
		
		self.usageLimit = self.theBoard.dictionary.difficultyToUsage(theDifficulty)
		
		print str(theDifficulty)+", "+str(self.usageLimit)
		
		if theHeuristic == None:
			self.heuristic = heuristic.Heuristic()
		else:
			self.heuristic = theHeuristic
		
		#start with a full set of tiles
		self.grab()
		
	'''
	Returns False if the player tries to draw new tiles and none exist in the bag (i.e. the
	game is finished), True if either tiles were successfully removed, or the tray isn't empty 
	'''	
	def grab(self):
		
		if not self.theBag.isEmpty() :
			
			#Attempt to withdraw the needed number of tiles
			numNeeded = Player.TRAY_SIZE-len(self.tray)
			for i in range(numNeeded):
				newTile = self.theBag.grab()
				if newTile != None:
					self.tray.append(newTile)
			
		#If the bag was empty AND our tray is empty, signal that play is over		
		elif len(self.tray) == 0:
			return False
			
		return True
		
	'''
	This function assumes the word was placed on the board by some mechanism as
	tentative tiles. The board then plays the tentative tiles, locking them if
	they work, returning them as a list if they don't. In the latter case, put
	the words back on the tray, in the former add the points and grab new tiles
	
	Returns True if the move was executed successfully (thus ending our turn) and
	False if it wasn't, forcing us to try again
	
	'''	
	def play(self, firstTurn):
		
		(tiles, points) = self.theBoard.play(firstTurn)
		
		#The play was successful, add the points to our score and grab new tiles
		if tiles == None and points >= 0:
			self.score += points
			self.lastScore = points
			gameContinues = self.grab()
			if gameContinues:
				return True
			else:
				return "END"
			
		#Play didn't work, put the
		elif tiles != None:		
			#take the tiles back
			for t in tiles:
				self.take(t)
				assert len(self.tray) <= Player.TRAY_SIZE
				
			return False
		
		#Simple case, we tried to play, but there were no tentative tiles!
		else:
			return False	
			
	'''
	Takes a tile previously held, should only be called for returning tentative pieces to the tray
	'''
	def take(self, tile):
		assert(len(self.tray) < Player.TRAY_SIZE)
		if tile.isBlank:
			tile.letter = ' '
		self.tray.append(tile)			
			
	'''
	Puts the tray back in the bag, shuffles the bag and withdraws new tiles
	'''		
	def shuffle(self):
		for tile in self.tray:
			self.theBag.putBack(tile)
		
		self.tray = []
		self.theBag.shuffle()
		self.grab()
	
	'''
	Prototype for Draw Tray, it does nothing by default, but a Human player will draw
	the tiles
	'''		
	def drawTray(self, DISPLAYSURF):
		return None		
		
	'''
	Returns the value of the players tray in points
	'''
	def trayValue(self):
		value = 0
		for tile in self.tray:
			value += tile.points
		return value
		
	'''
	Gives the points to the player
	'''
	def givePoints(self, num):
		self.score += num
			
	'''
	Accessor for score
	'''
	def getScore(self):
		return score
		
	'''
	Pulses the last score value for the player so we can see per-turn points
	'''
	def pulseScore(self):
		self.lastScorePulse = time.time()
		
	#------------------- AI -------------------------
	
	'''
	Calculates a good move and places the tiles on the board tentatively.
	Play should be called thereafter.
	
	Algorithm description:
		Since this is the heart of the AI, it deserves a brief description.
		I'm starting out with a brute-force method before I look into whether
		optimizations can be made because, if it doesn't take to long this algorithm
		will correctly provide the highest scoring move.
		
		Here's how it determines the best move in the possible moves space:
		
		1) 	First, it creates a list of seed positions. If this is the first turn
			we only have one (7,7) otherwise it is all unoccupied squares which are
			adjacent to an occupied one.
		2)	For each seed position, we run the following calculations for horizontal
			and vertical directions.
		3)	For each seed-direction, we create a list, tileSlots, which stores lists
			of tiles to place. We do this by 'growing' the word lower and higher to
			get all combinations of tile slots used. Growth automatically skips pre-played
			tiles and doesn't add placements which have tile slots out of bounds
		4)  For each set of tile slots, we run through all permutations of possible tiles
			to place in each slot. For each of these we run a board validation routine
			which tells us whether the move is correct and what score will result
		
	'''	
	def executeTurn(self, isFirstTurn, DISPLAYSURF):
		
		#Calculate turn execution time and output tray		
		startTime = time.time()
		if board.Board.DEBUG_ERRORS:
			self.maxWordTimeStamp = startTime
			self.validationTime = 0
			self.theBoard.dictionary.resetLookupTime()
			self.theBoard.resetAllMetrics()
			print [tile.letter for tile in self.tray]
			self.theWordsConsidered = ""
			self.maxScore = -1
				
		
		#STEP ONE: Create a list of seed positions
		seeds = []
		if isFirstTurn:
			seeds.append((7,7)) #The seed has to be (7,7) for the first turn
		
		else:	
			#find all empty adjacent squares and add them to the list	
			for x in range(board.Board.GRID_SIZE):
				for y in range(board.Board.GRID_SIZE):
					if self.theBoard.squares[x][y][0] != None:
						#UP
						if y > 0 and self.theBoard.squares[x][y-1][0] == None:
							if not (x, y-1) in seeds:
								seeds.append((x, y-1))
						#DOWN
						if y < board.Board.GRID_SIZE-1 and self.theBoard.squares[x][y+1][0] == None:
							if not (x, y+1) in seeds:
								seeds.append((x, y+1))
						#LEFT
						if x > 0 and self.theBoard.squares[x-1][y][0] == None:
							if not (x-1, y) in seeds:
								seeds.append((x-1, y))
						#RIGHT
						if x < board.Board.GRID_SIZE-1 and self.theBoard.squares[x-1][y][0] == None:
							if not (x+1, y) in seeds:
								seeds.append((x+1, y))
		
		#This will contain the best single-turn play possible						
		(maxPoints, maxTiles) = -1000, None		
		self.numValidations = 0
		self.numRawValidations = 0
		
		tileSlots = []				
								
		#STEP TWO: Run through each seed position and calculate both horz/vertical:
		for (x, y) in seeds:
			
			for lo in range(0, len(self.tray)):
				for hi in range(0, len(self.tray)-lo):
					
					#Build a horizontal tileSlot
					horz = [((x, y), self.theBoard.squares[x][y][0])]
					loCount = 0
					hiCount = 0
					xPos, yPos = x-1, y
					#Build left
					while xPos > 0 and (loCount < lo or self.theBoard.squares[xPos][yPos][0] != None):
						loCount += 1
						horz.insert(0, ((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						xPos -= 1
					#Build right
					xPos, yPos = x+1, y
					while xPos < board.Board.GRID_SIZE-1 and (hiCount < hi or self.theBoard.squares[xPos][yPos][0] != None):
						hiCount += 1
						horz.append(((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))	
						xPos += 1	
					
					#Build a vertical tileSlot
					vert = [((x, y), self.theBoard.squares[x][y][0])]
					loCount = 0
					hiCount = 0
					xPos, yPos = x, y-1
					#Build up
					while yPos > 0 and (loCount < lo or self.theBoard.squares[xPos][yPos][0] != None):
						loCount += 1
						vert.insert(0, ((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						yPos -= 1
					#Build down
					xPos, yPos = x, y+1
					while yPos < board.Board.GRID_SIZE-1 and (hiCount < hi or self.theBoard.squares[xPos][yPos][0] != None):
						hiCount += 1
						vert.append(((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						yPos += 1
						
					tileSlots.append(horz)
					tileSlots.append(vert)					
			
		
		#Now that we've developed tileSlots for each seed, let's discard all duplicates originating from different seeds
		tileSlotsMap = {}	# This hashes (x1,y1,x2,y2) to True if there is a tileslot with those bounds
		i = 0
		originalSize = len(tileSlots)
		numEliminated = 0
		while i < len(tileSlots):
			slot = tileSlots[i]
			(x1, y1) = slot[0]
			(x2, y2) = slot[-1]
			if tileSlotsMap.get((x1,y1,x2,y2), False):
				tileSlots.pop(i)
				numEliminated += 1
			else:
				tileSlotsMap[(x1,y1,x2,y2)] = True
				i += 1
				
		tileSlots = self.reorderTileSlots(tileSlots)		
				
		if board.Board.DEBUG_ERRORS:
			initTime = time.time()-startTime	
			print "Considering: "	
					
		#Now tileSlots should contain all possible tile slots, from that seed position
		progress = 0
		totalProgress = len(tileSlots)
		for tileSlot in tileSlots:
			progress += 1
			emptySlots = []
			wordBuilt = []
			slotPosition = {}
			for (x, y), tile in tileSlot:
				slotPosition[(x, y)] = True
				if tile == None:
					emptySlots.append((x,y))
				wordBuilt.append(tile)
			
			self.updateProgressBar(1.0*progress/totalProgress, DISPLAYSURF)
			
			timeSpent = time.time() - startTime
			
			if timeSpent > Player.TIMEOUT:
				
				
				break
				
			(points, tiles, blanks) = self.tryEverything(isFirstTurn, wordBuilt, emptySlots, self.tray)
			if points > maxPoints:
				(maxPoints, maxTiles, maxBlanks) = (points, tiles, blanks)
				
					
		#Now we should have the best tiles so play them
		if maxTiles != None and maxTiles != []:
			self.placeTiles(maxTiles, maxBlanks)
			playedMove = True
			
			seedRatio = self.theBoard.calculateSeedRatio()
			print "Seed Ratio: "+str(seedRatio)
			
			#Update statistics about the play made
			if board.Board.DEBUG_ERRORS:
				Player.aiStats.updateTiming(time.time()-startTime, self.maxWordTimeStamp-startTime)
				lettersUsed = []
				for pos, tile in maxTiles:
					if tile.isBlank:
						theLetter = "_"
					else:
						theLetter = tile.letter
					lettersUsed.append(theLetter)
				Player.aiStats.updateLetterPlays(lettersUsed, maxPoints)
				Player.aiStats.updateSeedRatio(seedRatio, maxPoints)
				Player.aiStats.save()
			
		#If there was truly NO move the computer could make, doesn't play anything
		else:
			playedMove = False
			
		if board.Board.DEBUG_ERRORS:
			endTime = time.time()
			timeSpent = endTime-startTime + .00001
			percentValidating = 100.0 * self.validationTime / timeSpent
			percentLookup = 100.0 * self.theBoard.dictionary.lookupTime / timeSpent
			percentInitializing = 100.0 * initTime / timeSpent
		
			totalValidationTime = (self.theBoard.quickValidationTime + self.theBoard.crosswordValidationTime +
									self.theBoard.dictionaryValidationTime + self.theBoard.scoringTime) + .00001
			percentQuickValidation = self.theBoard.quickValidationTime / totalValidationTime
			percentCrosswordValidation = self.theBoard.crosswordValidationTime / totalValidationTime
			percentDictionaryValidation = self.theBoard.dictionaryValidationTime / totalValidationTime
			percentScoring = self.theBoard.scoringTime / totalValidationTime
		
			print "AI: Wordsmith--Stats"
			print "--------------------"
			print "\t"+str(timeSpent)+" seconds required, of which,"
			print "\t\t"+str(percentInitializing)+" percent was spent initializing seed positions."
			print "\t\t"+str(percentValidating)+" percent was spent validating, in total."
			print "\t\t"+str(percentLookup)+" percent was spent on dictionary lookups."
			print "\t"+str(len(seeds))+" number of seed positions considered."
			print "\t"+str(100.0*self.numValidations/(self.numRawValidations+1) - 100)+" percent complexity increase due to blanks."
			print "\t"+str(self.numValidations)+" validations."
			print "\t"+str(self.numValidations - self.theBoard.invalidWordCount)+" of those plays were possible."
			print "\t"+str(self.theBoard.crosswordErrors)+" errors from invalid crossword formation."
			print "\t"+str(1.0*self.numValidations/(len(tileSlots)+1))+" average validations per slot."
			print "\t"+str(len(tileSlots))+" slot sets considered."
			print "\t"+str(100.0 * numEliminated/originalSize)+" percent reduction by using trimming."
			print "\tValidation details:"
			print "\t\tQuick validation: "+str(percentQuickValidation)
			print "\t\tCrossword generation: "+str(percentCrosswordValidation)
			print "\t\tDictionary validation: "+str(percentDictionaryValidation)
			print "\t\tScoring: "+str(percentScoring)
			print "--------------------"
			#print "Considered the following main words, when making a choice"
			#print self.theWordsConsidered
			
		return playedMove	 
			
	'''
	Given a set of positions, this will try every possible combination of tray tiles that could be inserted
	and return the score and tiles placed of the highest scoring combination by asking the board
	'''		
	def tryEverything(self, isFirstTurn, word, slots, trayTiles, tilesPlaced = []):
		
		#BASE CASE, we've placed every piece so validate and return the (score, tilesPlaced) tuple
		if len(slots) == 0:
		
			if board.Board.DEBUG_ERRORS:	#Some quick metrics for analyzing the algorithm
				startValidation = time.time()
			
			blankAssignment = []
			seedRatio = (-1, -1)
				
			#Before we go through complete validation, let's check the first word quickly for error
			i = 0
			spelling = ""
			for tile in word:
				
				if tile != None:
					spelling += tile.letter
				else:
					spelling += tilesPlaced[i][1].letter
					i+=1
					
			#If there are no blanks, we can go right ahead and evaluate		
			if not ' ' in spelling:		
				if self.theBoard.dictionary.isValid(spelling, self.usageLimit) or len(slots) == 1:
					if board.Board.DEBUG_ERRORS:
						self.numValidations += 1
						self.numRawValidations += 1
						if self.numValidations % 10 == 0:
							self.theWordsConsidered += "\n"
						self.theWordsConsidered += spelling + ", "
					(score, dummy, seedRatio) = self.theBoard.validateWords(isFirstTurn, tilesPlayed=tilesPlaced, vocabulary = self.usageLimit)
				else:
					score = -1000
			
			#Otherwise, we need to try to find a letter choice that works		
			else:
				#Get all blank assignments that correspond to real words
				blankAssignments = self.theBoard.dictionary.matchWithBlanks(spelling, vocabulary = self.usageLimit)
			
				rawValidation = 0
			
				if len(blankAssignments) > 0:
					for assignment in blankAssignments:
						
						#Apply the assignment to the blanks
						i = 0
						assignedSpelling = ''
						for (x, y), tile in tilesPlaced:
							if tile.isBlank:
								tile.letter = assignment[i]
								i += 1
							assignedSpelling += tile.letter
						
						if board.Board.DEBUG_ERRORS:
							self.numValidations += 1
							rawValidation = 1
							if self.numValidations % 10 == 0:
								self.theWordsConsidered += "\n"
							self.theWordsConsidered += assignedSpelling + ", "
							
						(score, dummy, seedRatio) = self.theBoard.validateWords(isFirstTurn, tilesPlayed=tilesPlaced, vocabulary = self.usageLimit)
						
						#We only need the first word that works, all others will have the same points
						if score > 0:
							blankAssignment = assignment
							break
							
				#No blank assignments validated the principle word
				else:
					score = -1000
					
				if board.Board.DEBUG_ERRORS:
					self.numRawValidations += rawValidation
					
			if board.Board.DEBUG_ERRORS:
				endValidation = time.time()
				self.validationTime += endValidation-startValidation
				
			score += self.heuristic.adjust(trayTiles = self.tray, playTiles = tilesPlaced, seedRatio = seedRatio)	
				
			if score > self.maxScore:
				self.maxScore = score
				self.maxWordTimeStamp = time.time()
		
			return (score, tilesPlaced, blankAssignment)
		
		#RECURSIVE CASE: Try applying all possible tiles to the slot, return the maximimum score
		else:
			slot = slots[0]
			(maxScore, maxTiles, maxBlanks) = (-1000, None, None)
			for tile in trayTiles:
				newTilesPlaced = tilesPlaced[:]
				newTilesPlaced.append((slot, tile))
				trayRemaining = trayTiles[:]
				trayRemaining.remove(tile)
				(score, tilesTried, blankAssignment) = self.tryEverything(isFirstTurn, word, slots[1:], trayRemaining, newTilesPlaced)
				if score > maxScore:
					maxScore, maxTiles, maxBlanks = score, tilesTried, blankAssignment
			return (maxScore, maxTiles, maxBlanks)
	
	'''
	Reorders the tile slots so as to (hopefully) find the max word earlier in the data processing so
	that if we time out the function arbitrarily, we'll get better results
	'''
	def reorderTileSlots(self, tileSlots):
		# We'll counting sort the tileSlots by # of empty slots
		# i.e. orderedBySlots[3] = all tileSlots with 3 empty slots
		orderedBySlots = [[] for i in range(Player.TRAY_SIZE+1)]
		
		for tileSlot in tileSlots:
			i = 0
			for pos, slot in tileSlot:
				if slot == None:
					i += 1
			assert i < len(orderedBySlots)	
			orderedBySlots[i].append(tileSlot)
		
		newTileSlots = []	
		for ranking in orderedBySlots:
			if len(ranking) > 0:
				for tileSlot in ranking:
					newTileSlots.append(tileSlot)
					
		return newTileSlots
		
	'''
	Given a set of tiles, this will automatically apply the tiles to the board as tentative pieces
	and remove them from the AI's tray
	'''
	def placeTiles(self, tiles, blanks):
		
		i = 0
		for (pos, tile) in tiles:
			
			if tile.isBlank and blanks != None and i < len(blanks):
				tile.letter = blanks[i]
				i+=1
						
			self.theBoard.setPiece(pos,tile)
			tile.pulse()
			self.tray.remove(tile)
					
			
	'''
	Updates the progress bar
	'''
	def updateProgressBar(self, progress, DISPLAYSURF):
		progText = Player.FONT.render("Thinking...", True, Player.FONT_COLOR, Player.BACKGROUND_COLOR)
		progRect = progText.get_rect()
		progRect.left = Player.PROGRESS_LEFT
		progRect.top = Player.PROGRESS_TOP
		DISPLAYSURF.blit(progText, progRect)	
		pygame.draw.rect(DISPLAYSURF, Player.PROGRESS_COLOR_BACK, (Player.PROGRESS_LEFT, Player.PROGRESS_TOP + Player.PROGRESS_MARGIN, Player.PROGRESS_WIDTH, Player.PROGRESS_HEIGHT))
		width = progress * Player.PROGRESS_WIDTH
		pygame.draw.rect(DISPLAYSURF, Player.PROGRESS_COLOR_FRONT, (Player.PROGRESS_LEFT, Player.PROGRESS_TOP + Player.PROGRESS_MARGIN, width, Player.PROGRESS_HEIGHT))
	
		pygame.display.update()