'''
This will store any menus all inherited from a prototype with two functions
update and execute. Update will change display based on cursor position, while
execute will process button clicks.
'''

import pygame, ai
from pygame.locals import *
from scrabble import DISPLAYSURF, CLICK

class Menu():
	
	def __init__(self):
		self.buttons = {}
		self.rect = (0, 0, 800, 600)
		self.background = (255, 255, 255)
	
	'''
	Goes through all buttons and returns the name of the button, if it was clicked
	'''
	def execute(self, mouseX, mouseY):
		if self.within(mouseX, mouseY):
			theKey = ""
			for key in self.buttons.keys():
				if self.buttons[key].within(mouseX, mouseY):
					theKey = key
		
			if theKey != "":
				CLICK.play()
					
			return theKey
	
	'''
	Goes through and updates all buttons, redrawing them if they are hovered
	'''	
	def update(self, mouseX, mouseY):
		for button in self.buttons.values():
			button.update(mouseX, mouseY)
			
	def within(self, mouseX, mouseY):
		(left, top, width, height) = self.rect
		return mouseX >= left and mouseX <= left+width and mouseY >= top and mouseY <= top+height	
		
	def redraw(self):
		pygame.draw.rect(DISPLAYSURF, self.background, self.rect)
		for button in self.buttons.values():
			button.redraw()		

#==================== MAIN MENU =====================
		
class MainMenu(Menu):
	
	NEW_GAME = "new"
	EXIT_GAME = "exit"
	TRAINING = "training"
	ACHIEVEMENT = "achievement"
	
	def __init__(self, userdata):
		Menu.__init__(self)
		trainerText = TextBox(["Practice your Scrabble skills with a built-in HINT",
								"box, which lets you know how the AI would have played",
								"your move. But you can't get ACHIEVEMENTS while training."], (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		newGameText = TextBox(["Play one-on-one against Wordsmith, the Scrabble AI.",
							    "No hints allowed, try to beat your best score!"], (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		achieveText = TextBox(self.createAchievementText(userdata), (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		self.buttons[MainMenu.TRAINING] = Button("Training", (250, 135, 300, 50), trainerText)
		self.buttons[MainMenu.NEW_GAME] = Button("Challenge", (250, 190, 300, 50), newGameText)
		self.buttons[MainMenu.ACHIEVEMENT] = Button("Achievements", (250, 245, 300, 50), achieveText)
		self.buttons[MainMenu.EXIT_GAME] = Button("Exit", (250, 300, 300, 50))
		DISPLAYSURF.fill((255,255,255))
		
	def resetAchievements(self, userdata):
		self.buttons[MainMenu.ACHIEVEMENT].textBox.text = self.createAchievementText(userdata)
		
	def createAchievementText(self, userdata):
		text = []
		if userdata.has_key("name"):
			text.append(userdata["name"]+"'s Achievements")
		else:
			text.append("Guest Achievements")

		if userdata.has_key("bestScore"):
			text.append("Highest Score: "+str(userdata["bestScore"]))
		else:
			text.append("Highest Score: 0")	

		if userdata.has_key("numVictories"):
			text.append("Victories: "+str(userdata["numVictories"]))
		else:
			text.append("Victories: 0")

		if userdata.has_key("numGames"):
			text.append("Games Played: "+str(userdata["numGames"]))
		else:
			text.append("Games Played: 0")	
			
		return text
		
		
#==================== GAME MENU =====================

class GameMenu(Menu):

	PLAY_TURN = "play"
	RESHUFFLE = "shuffle"
	MAIN_MENU = "quit"
	HINT_TURN = "hint"

	def __init__(self, useHintBox = False):
		Menu.__init__(self)
		self.rect = (570, 300, 150, 300)
		playText = TextBox(["Confirm your move,",
							"returns your tiles if",
							"your move is illegal."], (570, 480), (55, 46, 40), (255, 255, 255))
		self.buttons[GameMenu.PLAY_TURN] = Button("PLAY", (570, 300, 150, 30), textBox = playText)
		shuffleText = TextBox(["Forfeit your turn",
							"and draw new tiles for",
							"the next turn."], (570, 480), (55, 46, 40), (255, 255, 255))
		self.buttons[GameMenu.RESHUFFLE] = Button("REDRAW", (570, 340, 150, 30), textBox = shuffleText)
		if useHintBox:
			hintText = TextBox(["The AI will put your",
								"pieces down. Just hit",
								"PLAY to confirm it."], (570, 480), (55, 46, 40), (255, 255, 255))
			self.buttons[GameMenu.HINT_TURN] = Button("HINT", (570, 380, 150, 30), textBox = hintText, color = (255, 255, 100), backColor = (255, 170, 50))
			self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 420, 150, 30))
		else:
			self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 380, 150, 30))
		DISPLAYSURF.fill((255,255,255))		
		
#==================== TEXT BOX ======================
class TextBox():
	
	initialized = False
	MARGIN = 21
	
	@staticmethod
	def initialize():
		TextBox.FONT = pygame.font.Font('freesansbold.ttf', 18)
		TextBox.initialized = True
		

	def __init__(self, textLines, pos, color, backColor, horzCenter = False):	
		self.text = textLines
		self.pos = pos
		self.color = color
		self.width = 0
		self.backColor = backColor
		self.horzCentered = horzCenter
		if not TextBox.initialized:
			TextBox.initialize()
		
	def draw(self):	
		i = 0
		for	line in self.text:
			left = self.pos[0]
			top = self.pos[1] + TextBox.MARGIN * i
			text = TextBox.FONT.render(line, True, self.color, self.backColor)
			rect = text.get_rect()
			if self.horzCentered:
				rect.centerx = left
			else:
				rect.left = left
			rect.top = top
			if rect.width > self.width:
				self.width = rect.width
			DISPLAYSURF.blit(text, rect)		
			i+=1
			
	def undraw(self):
		height = TextBox.MARGIN * len(self.text)
		if self.horzCentered:
			rect = (self.pos[0]-self.width/2, self.pos[1], self.width, height)
		else:
			rect = (self.pos[0], self.pos[1], self.width, height)
		pygame.draw.rect(DISPLAYSURF, self.backColor, rect)	
		
#==================== BUTTON ========================

class Button():
	
	BACKGROUND = (125, 125, 170)
	HIGHLIGHT = (200, 200, 255)
	FONT_COLOR = (55, 46, 40)
	
	ON = "on"
	OFF = "off"
	
	initialized = False

	@staticmethod
	def initialize():
		Button.FONT = pygame.font.Font('freesansbold.ttf', 18)
		Button.initialized = True
	
	def __init__(self, name, rect, textBox = None, color = None, backColor = None):
		#Make sure the fonts are set up
		if not Button.initialized:
			Button.initialize()
			
		if color == None:
			color = Button.HIGHLIGHT
		if backColor == None:
			backColor = Button.BACKGROUND
		
		self.name = name
		self.rect = rect
		self.lastDrawn = Button.OFF
		self.textBox = textBox
		self.color = color
		self.backColor = backColor
	
	def update(self, mouseX, mouseY):
		
		if self.within(mouseX, mouseY):
			self.draw(self.color)
			self.lastDrawn = Button.ON
			if self.textBox != None:
				self.textBox.draw()
		else:
			self.draw(self.backColor)
			if self.lastDrawn == Button.ON and self.textBox != None:
				self.textBox.undraw()
			self.lastDrawn = Button.OFF
			
	def within(self, mouseX, mouseY):
		(left, top, width, height) = self.rect
		return mouseX >= left and mouseX <= left+width and mouseY >= top and mouseY <= top+height
		
	def draw(self, backColor):
		pygame.draw.rect(DISPLAYSURF, backColor, self.rect)
		(left, top, width, height) = self.rect	
		text = Button.FONT.render(self.name, True, Button.FONT_COLOR, backColor)
		rect = text.get_rect()
		rect.center = (left+width/2, top+height/2)
		DISPLAYSURF.blit(text, rect)
		
	def redraw(self):
		if self.lastDrawn == Button.ON:
			self.draw(self.color)
		elif self.lastDrawn == Button.OFF:
			self.draw(self.backColor)
			