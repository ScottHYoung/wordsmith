#This is the main scrabble program
'''
Scrabble To-Do:

	- Make processing time delay as a function
	- Have generic "Player" account with achievements
	
Heuristic ideas:

	IDEA: Conserved play of high letters Q, Z, J, X
	- Figure out word score 'bonus' for high-letter tiles, on average
	
	IDEA: Conserved play of flexible letters S and BLANK
	- Figure out average word score 'bonus' for having a blank or S
	
	IDEA: Open plays (which create significantly more seed positions) should be discouraged
	- Store the seed list and update it with tile slots, deduct points for words which add too much
	
	IDEA: Hanging plays (which create advantageous seed positions) should be penalized
	- For each new seed generated (and subtracted for each seed removed) figure out the 
	  letter and words scores accessible and subtract points

'''


import pygame, random, sys, time
from pygame.locals import *

#local files
import board, tile, bag, player, human, ai, heuristic

pygame.init()

#window setup
DISPLAYSURF = pygame.display.set_mode((800, 600))
ALPHASURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption('Wordsmith!')

tile.Tile.initialize()

#Simple sound effects
TIC = pygame.mixer.Sound('media/tic.ogg')
TICTIC = pygame.mixer.Sound('media/tictic.ogg')
DINGDING = pygame.mixer.Sound('media/dingding.ogg')
SCRIFFLE = pygame.mixer.Sound('media/scriffle.ogg')
CLICK = pygame.mixer.Sound('media/click.ogg')

#Achievements and data
USERFILE = 'media/user.txt'

#IMPORT THE MENU
import menu


#font setup
SCORE_FONT = pygame.font.Font('freesansbold.ttf', 20)
SCORE_LEFT = 570
SCORE_TOP = 100
SCORE_MARGIN = 25
SCORE_PULSE = 5.0

BACKGROUND_COLOR = (255, 255, 255)
SCORE_COLOR = (55, 46, 40)

#GAME MODES
TRAINING_FLAG = False #With this set to true, entering training mode causes the AI to play against
					  #itself automatically
					
if TRAINING_FLAG:
	TIC.set_volume(0.0)
	TICTIC.set_volume(0.0)
	DINGDING.set_volume(0.0)
	SCRIFFLE.set_volume(0.0)
	CLICK.set_volume(0.0)



##=====================MAIN======================
def main():
	USERDATA = loadUser()
	
	theMenu = menu.MainMenu(USERDATA)
	while True:
		mouseClicked = False	
		mouseMoved = False
		SELECTION = ""	
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY = event.pos
				mouseMoved = True
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True
				
		if mouseClicked:
			SELECTION = theMenu.execute(mouseX, mouseY)
			
		if mouseMoved:
			theMenu.update(mouseX, mouseY)
			
		if SELECTION == menu.MainMenu.NEW_GAME:
			USERDATA["numGames"] += 1
			saveUser(USERDATA)
			theMenu.resetAchievements(USERDATA)
			runGame(USERDATA)
			theMenu.resetAchievements(USERDATA)
			theMenu.redraw()
		elif SELECTION == menu.MainMenu.TRAINING or TRAINING_FLAG:
			runGame(USERDATA, useHintBox=True)
			theMenu.redraw()
		elif SELECTION == menu.MainMenu.EXIT_GAME:
			pygame.quit()
			sys.exit()
			
		pygame.display.update()


	
def runGame(USERDATA, useHintBox = False):	
	theBag = bag.Bag()
	
	theBoard = board.Board()
	
	players = []
	
	h = heuristic.notEndGameHeuristic(heuristic.tileQuantileHeuristic(.5, 1.0))
	
	players.append(human.Human("Player", theBoard, theBag))
	players.append(ai.AI(theBoard, theBag, theHeuristic = h, theDifficulty = 10.0))
	#players.append(ai.AI(theBoard, theBag))
	
	active = 0
	
	computerTurn = isinstance(players[active], ai.AI)	
	firstTurn = True
	gameOver = False
	
	
	gameMenu = menu.GameMenu(useHintBox)
	
	redrawEverything(theBoard, players[active], players, gameOver, gameMenu)
	
	inHand = None
	stillPlaying = True
	AIstuck = False
	
	while stillPlaying:
		
		mouseClicked = False
		mouseMoved = False
		actionKeyHit = False
		shuffleKeyHit = False
		hintKeyHit = False
		
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY = event.pos
				mouseMoved = True
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True
			elif event.type == KEYUP:
				if event.key == K_SPACE or event.key == K_RETURN:
					actionKeyHit = True
				if event.key == K_r:
					shuffleKeyHit = True
				if event.key == K_h and useHintBox:
					hintKeyHit = True
					
		#GAME MENU BUTTONS	
		if mouseMoved:
			gameMenu.update(mouseX, mouseY)

		if mouseClicked:
			SELECTION = gameMenu.execute(mouseX, mouseY)	

			if SELECTION == menu.GameMenu.PLAY_TURN:
				actionKeyHit = True
			elif SELECTION == menu.GameMenu.RESHUFFLE:
				shuffleKeyHit = True
			elif SELECTION == menu.GameMenu.HINT_TURN:
				hintKeyHit = True
			elif SELECTION == menu.GameMenu.MAIN_MENU:
				stillPlaying = False
				
		if (hintKeyHit or TRAINING_FLAG) and not computerTurn and not gameOver:
			tilesPulled = theBoard.removeTempTiles()
			if tilesPulled != None:		
				#take the tiles back
				for t in tilesPulled:
					players[active].take(t)
			players[active].executeTurn(firstTurn, DISPLAYSURF)
			TICTIC.play()									
					
		if (actionKeyHit or TRAINING_FLAG or computerTurn) and not gameOver:
			#If it's the computer turn, we need to process its move first!
			if computerTurn:
				playedMove = players[active].executeTurn(firstTurn, DISPLAYSURF)
			else:
				playedMove = True
			
			if playedMove:	
				
				success = players[active].play(firstTurn)
				if success == "END":
					gameOver = True
					endGame(players, active, useHintBox, USERDATA)
				elif success:
					DINGDING.play()
					players[active].pulseScore()
					firstTurn = False
					active += 1
					if active >= len(players):
						active = 0
					computerTurn = isinstance(players[active], ai.AI)
					#If we were stuck before, we aren't anymore
					if computerTurn:
						AIstuck = False					
				else:
					if TRAINING_FLAG:
						AIstuck = True
					TICTIC.play()
					if computerTurn:
						print "AI thinks it has a good move, but it doesn't"
			else:
				players[active].shuffle()
				#Let the player know the AI shuffled
				players[active].lastScore = 0
				players[active].pulseScore()
				if theBag.isEmpty():
					AIstuck = True
					
				active += 1
				if active >= len(players):
					active = 0
				computerTurn = isinstance(players[active], ai.AI)

			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	
			
		if (shuffleKeyHit or (AIstuck and TRAINING_FLAG)) and not computerTurn and not gameOver:
			SCRIFFLE.play()
			players[active].shuffle()
			active += 1
			if active >= len(players):
				active = 0
			computerTurn = isinstance(players[active], ai.AI)
			#If we're stuck AND the AI is stuck, end the game without subtracting points
			if AIstuck:
				gameOver = True
				endGame(players, active, useHintBox, USERDATA, stuck = True)
			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)
			
				
			
		if mouseClicked and not computerTurn and not gameOver:
			inHand = tileGrab(mouseX, mouseY, inHand, theBoard, players[active])
			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	
			
		if gameOver and TRAINING_FLAG: #automatically start a new game for training purposes
			stillPlaying = False

		redrawNecessary(theBoard, players, gameOver)		
		pygame.display.update()
##===============================================
'''
This resolves the action of the player to try to pick up a tile. Two situations:
1) The player has a piece in hand:
	-If it's on the board, attempt to place the piece there. If it doesn't work,
	 do nothing. If it does work, empty the hand and update the board
	-If it's on the tray, swap positions and set the hand to none
2) The player doesn't have a piece in hand:
	-If it's on the board and the piece is not locked, return it to the tray (at the end)
	-If it's on the tray, highlight that piece and put it in hand.
'''
def tileGrab(x, y, hand, theBoard, theHuman):
	
	if hand == None:
		tile = theBoard.remove(x, y) # try to remove a piece from the board
		if tile != None:
			TIC.play()
			theHuman.take(tile)		# if it worked, put it back on our tray
			return None
		else:
			tile = theHuman.pickup(x, y) # if it didn't, try to remove from the tray
			if tile != None:
				return tile	 #if it worked, put the tile inHand (pickup will remember the held tile)
			else:
				return None  #hand stays empty
	else:
		(success, blank) = theBoard.placeTentative(x, y, hand) #try to place the tile on the board
		if success != False:
			TIC.play()
			if success == "ASK":
				theBoard.askForLetter(blank, DISPLAYSURF, ALPHASURF)
			theHuman.placeTentative()	#if it's successful place a tentative piece
			return None					#empty the hand
		else:
			tile = theHuman.pickup(x, y)	#otherwise try to swap the piece on the tray
			return tile
			

'''
Composite function which redraws everything
'''	
def redrawEverything(board, currentPlayer, players, gameOver, gameMenu):
	DISPLAYSURF.fill(BACKGROUND_COLOR)
	board.draw(DISPLAYSURF, ALPHASURF)
	currentPlayer.drawTray(DISPLAYSURF)	
	drawScore(players, gameOver)
	gameMenu.redraw()
	
'''
Function which redraws only animated elements
'''	
def redrawNecessary(board, players, gameOver):
	board.drawDirty(DISPLAYSURF, ALPHASURF)
	drawScore(players, gameOver)
		
'''
Draws the scores
'''
def drawScore(players, gameOver):
	i = 0
	left = SCORE_LEFT
	for player in players:
		top = SCORE_TOP + SCORE_MARGIN * i
		
		sentence = player.name + ": " + str(player.score)
		
		scoreText = SCORE_FONT.render(sentence, True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = top
		DISPLAYSURF.blit(scoreText, scoreRect)
		
		#Score Pulse
		if time.time() - player.lastScorePulse < SCORE_PULSE:
			tween = (time.time()-player.lastScorePulse) / SCORE_PULSE
			color = (SCORE_COLOR[0]*(1-tween) + BACKGROUND_COLOR[0]*tween,
					SCORE_COLOR[1]*(1-tween) + BACKGROUND_COLOR[1]*tween,
					SCORE_COLOR[2]*(1-tween) + BACKGROUND_COLOR[2]*tween)
			pulseText = SCORE_FONT.render("(+"+str(player.lastScore)+")", True, color, BACKGROUND_COLOR)
			pulseRect = pulseText.get_rect()
			pulseRect.left = scoreRect.right + 10
			pulseRect.top = top
			DISPLAYSURF.blit(pulseText, pulseRect)
				
		i += 1
	
	#Let players know the game is over!
	if gameOver:
		scoreText = SCORE_FONT.render("Game finished!", True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = SCORE_TOP + SCORE_MARGIN * i
		DISPLAYSURF.blit(scoreText, scoreRect)		
		
'''
Ends the game, taking the tray value from all unfinished players, subtracting the value
from their score and giving it to the active player (who just finished)
'''
def endGame(players, active, isPractice, userdata, stuck = False):
	
	#Do points swaps only if someone could finish
	if not stuck:
		i = 0
		surplus = 0
		for p in players:
			if i != active:
				value = p.trayValue()
				p.givePoints(-value)
				surplus += value
		players[active].givePoints(surplus)	
	
	if not isPractice:
		maxScore = -1
		maxPlayer = players[0]
		for p in players:
			if isinstance(p, human.Human):
				if userdata.has_key("bestScore") and p.score > userdata["bestScore"]:
					userdata["bestScore"] = p.score
			if p.score > maxScore:
				maxPlayer = p
				maxScore = p.score
			
		if isinstance(maxPlayer, human.Human):
			if userdata.has_key("numVictories"):
				userdata["numVictories"] += 1
			
		saveUser(userdata)
	
	if TRAINING_FLAG:
		player.Player.aiStats.saveGame([p.score for p in players])
		player.Player.aiStats.save()
	
	
def loadUser():
	userFile = open(USERFILE, 'r')
	i = 0
	userdata = {}
	userdata["name"] = "Guest"
	userdata["bestScore"] = 0
	userdata["numVictories"] = 0
	userdata["numGames"] = 0
	for line in userFile:
		line = line.rstrip()
		if i == 0:
			userdata["name"] = line
		elif i == 1:
			userdata["bestScore"] = int(line)
		elif i == 2:
			userdata["numVictories"] = int(line)
		elif i == 3:
			userdata["numGames"] = int(line)
			
		i += 1
			
	return userdata
	
def saveUser(USERDATA):
	userFile = open(USERFILE, 'w')
	if USERDATA.has_key("name"):
		userFile.write(str(USERDATA["name"])+"\n")
	else:
		userFile.write("Guest\n")
	
	if USERDATA.has_key("bestScore"):
		userFile.write(str(USERDATA["bestScore"])+"\n")
	else:
		userFile.write("0\n")	
		
	if USERDATA.has_key("numVictories"):
		userFile.write(str(USERDATA["numVictories"])+"\n")
	else:
		userFile.write("0\n")

	if USERDATA.has_key("numGames"):
		userFile.write(str(USERDATA["numGames"])+"\n")
	else:
		userFile.write("0\n")	

##===============================================
##===============================================
if __name__ == '__main__':
	main()