'''
This is a file which stores various statistics for AI metrics:
'''

import pygame, random, sys, time, math, dictionarywords
from pygame.locals import *

class AIStats():
	
	FILENAME = "media/aistats.txt"  #'media/heuristic/heuristic_tilequantile_5_5.txt'
	COLLECT_WORD_DATA = False		#if True, this will collect data on timing/letterPlays
	COLLECT_GAME_DATA = False		#if True, this will record data for entire games
	
	def __init__(self):
		
		self.timingInfo = []
		self.letterPlays = {}
		for code in range(ord('A'), ord('Z')+1):
			char = chr(code)
			self.letterPlays[char] = []
		#also add a count for blanks
		self.letterPlays["_"] = []
		self.scores = []
		
		self.seedRatio = []
		
		self.load()
	
	'''
	Loads all stats from last time to update
	'''
	def load(self):
		try:
			statsFile = open(AIStats.FILENAME, 'r')
			
			MODE = "none"
			for line in statsFile:
				
				if line != "\n":
					line = line.rstrip()
					if MODE == "TIMING:":
						tokens = line.split()
						#TIMING DATA should be [totalTime] [timeAtMaxWord]
						assert len(tokens) == 2
						self.timingInfo.append((float(tokens[0]) , float(tokens[1])))
					
					elif MODE == "LETTERS:":
						tokens = line.split()
						#LETTER PLAY should be [letter] [score]
						assert len(tokens) == 2
						self.letterPlays[tokens[0]].append(float(tokens[1]))
						
					elif MODE == "SEED:":
						tokens = line.split()
						#SEEDS should be [numSeeds] [numTiles] [points]
						assert len(tokens) == 3
						self.seedRatio.append((int(tokens[0]), int(tokens[1]), float(tokens[2])))						
						
					elif MODE == "GAME:":
						tokens = line.split()
						self.scores.append([int(token) for token in tokens])
						
						

				else:
					MODE = "none"
								
				if line == "TIMING:":
					MODE = "TIMING:"
				elif line == "LETTERS:":
					MODE = "LETTERS:"
				elif line == "SEED:":
					MODE = "SEED:"
				elif line == "GAME:":
					MODE = "GAME:"
					
		except IOError as e:
			pass
	
	'''
	Saves all stats
	'''		
	def save(self):
		statsFile = open(AIStats.FILENAME, 'w')
		
		statsFile.write("TIMING:\n")
		for timeStamp in self.timingInfo:
			statsFile.write(str(timeStamp[0])+" "+str(timeStamp[1])+"\n")
		statsFile.write("\n")
			
		statsFile.write("LETTERS:\n")
		for code in range(ord('A'), ord('Z')+1):
			char = chr(code)
			if len(self.letterPlays[char]) > 0:
				for play in self.letterPlays[char]:
					statsFile.write(char+" "+str(play)+"\n")
		if len(self.letterPlays["_"]) > 0:
			for play in self.letterPlays["_"]:
				statsFile.write("_ "+str(play)+"\n")
		statsFile.write("\n")	
		
		statsFile.write("SEED:\n")
		for seeds in self.seedRatio:
			statsFile.write(str(seeds[0])+" "+str(seeds[1])+" "+str(seeds[2])+"\n")
		statsFile.write("\n")
		
		statsFile.write("GAME:\n")
		for game in self.scores:
			for score in game:
				statsFile.write(str(score)+" ")
			statsFile.write("\n")
		statsFile.write("\n")		
		
			
	def updateTiming(self, totalTime, timeAtMaxWord):
		if AIStats.COLLECT_WORD_DATA:
			self.timingInfo.append((totalTime, timeAtMaxWord))
		
	def updateLetterPlays(self, lettersUsed, points):
		if AIStats.COLLECT_WORD_DATA:
			for letter in lettersUsed:
				self.letterPlays[letter].append(points)
				
	def updateSeedRatio(self, (numSeeds, numTiles), points):
		if AIStats.COLLECT_WORD_DATA:
			self.seedRatio.append((numSeeds, numTiles, points))
				
	def saveGame(self, gameScores):
		if AIStats.COLLECT_GAME_DATA:
			self.scores.append(gameScores)
	
	'''
	Displays a histogram of the ratio of timeAtMaxWord over totalTime
	'''	
	def visualizeTiming(self, DISPLAYSURF):
		values = []
		for timeStamp in self.timingInfo:
			values.append(timeStamp[1]/(timeStamp[0]+0.00001))
		
		self.drawHistogram(DISPLAYSURF, values, 400, 400, 100)
	
	'''
	Gets the CDF of the timingInfo data, given a certain cutoff time, to see
	what percentage of turns would be executed properly
	'''	
	def timingCDF(self, cutoffTime):
		i = 0
		for totalTime, maxWordTime in self.timingInfo:
			if maxWordTime < cutoffTime:
				i += 1
				
		return i / (len(self.timingInfo) + 0.00001)
		
	'''
	Gets the inverse CDF of letterPlay info for one play, to determine what
	score and less accounts for percentMass of the data
	'''
	def letterPlaysInvCDF(self, letter, mass):
		assert mass >= 0.0 and mass <= 1.0
		if letter != None:
			plays = self.letterPlays[letter]
		else:
			plays = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				for play in self.letterPlays[char]:
					plays.append(play)
		score = -1
		if len(plays) > 0:
			plays = sorted(plays)
			score = plays[int(mass*len(plays))]
			
		return score
				
	
	'''
	Gets the average of a letterPlay
	'''		
	def letterPlaysMean(self, letter):
		total = 0
		if letter != None:
			plays = self.letterPlays[letter]
		else:
			plays = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				for play in self.letterPlays[char]:
					plays.append(play)
			
		for play in plays:
			total += play
		mean = total/(len(plays)+0.0001)
		return mean
		
	'''
	Gets the standard deviation of a letterPlay
	'''
	def letterPlaysStdDev(self, letter):
		total = 0
		mean = self.letterPlaysMean(letter)
		if letter != None:
			plays = self.letterPlays[letter]
		else:
			plays = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				for play in self.letterPlays[char]:
					plays.append(play)
		for play in plays:
			total += math.pow(play-mean, 2)
		variance = total/(len(plays)+0.0001)
		stddev = math.sqrt(variance)
		return stddev
		
	'''
	Gets the games won from the 1st player, to see the relative win %
	'''
	def getGamesWon(self):
		totalWon = 0
		for scores in self.scores:
			assert len(scores) == 2, "Error, function only works for 2-player games."
			if scores[0] > scores[1]:
				totalWon += 1
			elif scores[0] == scores[1]:
				totalWon += 0.5
				
		return totalWon
		
	'''
	Gets the mean of the difference Player 1 - Player 2 in game scores
	(assumes Heurstic v. Control)
	'''	
	def getGameDiffMean(self):
		totalDifference = 0
		for scores in self.scores:
			assert len(scores) == 2, "Error: function only works for 2-player games."
			difference = scores[0] - scores[1]
			totalDifference += difference
		
		return (totalDifference / len(self.scores))
		
	'''
	Gets the standard deviation of the difference Player 1 - Player 2 in game scores
	(assumes Heurstic v. Control)
	'''	
	def getGameDiffStdDev(self):
		totalDifference = 0
		mean = self.getGameDiffMean()
		for scores in self.scores:
			assert len(scores) == 2, "Error: function only works for 2-player games."
			difference = scores[0] - scores[1]
			totalDifference += math.pow(difference-mean, 2)
		
		totalDifference = math.sqrt(totalDifference)
		return (totalDifference / len(self.scores))		
		
	'''
	Gets the highest word score
	'''
	def getHighestWord(self, letter = None):
		if letter != None:
			plays = self.letterPlays[letter]
		else:
			plays = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				for play in self.letterPlays[char]:
					plays.append(play)
		
		return(max(plays))
	
	'''
	Normalizes all seedRatio data and draws the heat map
	'''	
	def visualizeSeedRatio(self, DISPLAYSURF, clamp=50):
		maxSeeds = 0
		maxTiles = 0
		maxScore = 0
		for seeds, tiles, score in self.seedRatio:
			if seeds > maxSeeds:
				maxSeeds = seeds
			if tiles > maxTiles:
				maxTiles = tiles
			if score > maxScore:
				maxScore = score
				
		values = []		
		for seeds, tiles, score in self.seedRatio:
			normSeeds = seeds / (maxSeeds + 0.00001)
			normTiles = tiles / (maxTiles + 0.00001)
			normScore = score / (clamp + 0.00001)
			
			assert (normSeeds >= 0.0 and normSeeds <= 1.0 and 
					normTiles >= 0.0 and normTiles <= 1.0)
			
			values.append((normSeeds, normTiles, normScore))
			
		self.drawHeatMap(DISPLAYSURF, values, 30)
		
		
	'''
	Draws a heatmap of a 3D data-set where x, y are ranged between 0.0 and 1.0,
	plotted values must range between 0.0 and 1.0, everything above and below is clamped.
	'''
	def drawHeatMap(self, DISPLAYSURF, values, size, blockSize = 10):
		
		#create a grid
		buckets = []
		for i in range(size):
			buckets.append([])
			for j in range(size):
				buckets[i].append([])
				
		for value in values:
			x = int(value[0] / (1.0/(size)))
			y = int(value[1] / (1.0/(size)))
			
			assert x >= 0 and x < len(buckets) and y >= 0 and y < len(buckets)
			
			buckets[x][y].append(value[2])
		
		LEFT_X = 10
		TOP_Y = 50
		for x in range(size):
			for y in range(size):
				total = 0.0
				num = 0.0001 #Add a small amount to the number so we don't get div by 0 errors
				for value in buckets[x][y]:
					#Clamp values
					if value > 1.0:
						value = 1.0
					elif value < 0.0:
						value = 0.0
					total += value	
					num += 1
				
				avg = (total/num)
				
				assert avg >= 0.0 and avg <= 1.0
				
				color = (255*avg, 255*avg, 255*avg)
				if num < 1.0:
					color = (0, 0, 0)
				
				left = LEFT_X + blockSize * x
				top = TOP_Y + blockSize * y
				
				pygame.draw.rect(DISPLAYSURF, color, (left, top, blockSize, blockSize))
				
	'''
	Shows a histogram of words by their Google n-gram usage value
	'''	
	def visualizeWordUsage(self, DISPLAYSURF):
		
		dictionary = dictionarywords.DictionaryWords("media/scrabblewords_usage.txt")
		
		values = dictionary.words.values()
		maxUsage = math.log(max(values))
					
		print "Most used word appeared "+str(maxUsage)+" times in Google's ngram corpus."
		
		normalizedValues = []
		
		for val in values:
			if val < 0:
				normalizedValues.append(math.log(1)/(maxUsage+1))
			else:
				normalizedValues.append(math.log(val)/(maxUsage+1))
				
		self.drawHistogram(DISPLAYSURF, normalizedValues, 400, 400, 10)		
	
	'''
	Gives the quantiles of word usages
	'''	
	def wordUsageQuantiles(self, quantiles):
		dictionary = dictionarywords.DictionaryWords("media/scrabblewords_usage.txt")
		
		values = dictionary.words.values()
		values.sort(reverse=True)
		for quantile in quantiles:
			
			massCutoff = int(quantile * len(values))
			
			assert massCutoff < len(values)
			
			point = values[massCutoff]
			if point <= 1:
				point = 1
			
			print str(quantile)+" = "+str(math.log(point))			
			
	'''
	Draws a histogram given a set of values ranging from 0.0 -> 1.0 and
	a width, height and number of buckets
	'''
	def drawHistogram(self, DISPLAYSURF, values, width, height, numBuckets):
		buckets = []
		for i in range(numBuckets):
			buckets.append(0)
			
		for value in values:
			assert value >= 0.0 and value <= 1.0, "Histogram only works on values between 0.0 and 1.0"
			
			bucketNumber = int(value / (1.0/(numBuckets)))
			
			assert bucketNumber >= 0 and bucketNumber < len(buckets)
			
			buckets[bucketNumber] += 1
			
		maxBucket = max(buckets)
		
		LEFT_X = 10
		TOP_Y = 50
		COLOR = (0, 100, 255)
		
		pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (LEFT_X, TOP_Y, width, height))
		
		i = 0	
		barWidth = width/numBuckets
		for bucket in buckets:
			barLeft = LEFT_X + i * barWidth
			barHeight = float(bucket)/maxBucket * height
			barTop = TOP_Y + (height - barHeight)
			pygame.draw.rect(DISPLAYSURF, COLOR, (barLeft, barTop, barWidth, barHeight))
			
			i += 1	

#RUNNING WORD FREQUENCY ON ITS OWN PROVIDES STATISTICS			
if __name__ == '__main__':
	
	aiStats = AIStats()
	
	print str(len(aiStats.timingInfo)) + " data points collected."
	
	#DISPLAYSURF = pygame.display.set_mode((800, 600))
	#pygame.display.set_caption('Wordsmith Statistics')
	#aiStats.visualizeTiming(DISPLAYSURF)
	#aiStats.visualizeSeedRatio(DISPLAYSURF)
	
	#aiStats.visualizeWordUsage(DISPLAYSURF)
	
	aiStats.wordUsageQuantiles([(i+1)/100.0 for i in range(99)])
	
	groupMedian = aiStats.letterPlaysInvCDF(None, .5)
	groupMean = aiStats.letterPlaysMean(None)
	group25p = aiStats.letterPlaysInvCDF(None, .25)
	group75p = aiStats.letterPlaysInvCDF(None, .75)
	groupStdDev = aiStats.letterPlaysStdDev(None)
	for code in range(ord('A'), ord('Z')+1):
		char = chr(code)
		print char+": \tmedian = "+str(aiStats.letterPlaysInvCDF(char, .5)-groupMedian)
		print "\tmean = "+str(aiStats.letterPlaysMean(char)-groupMean)
		print "\t25th percentile: "+str(aiStats.letterPlaysInvCDF(char, .25)-group25p)
		print "\t75th percentile: "+str(aiStats.letterPlaysInvCDF(char, .75)-group75p)
		print "\tStd dev: "+str(aiStats.letterPlaysStdDev(char)/groupStdDev)
		print "\tBest play ever: "+str(aiStats.getHighestWord(char))
		
	char = '_'	
	print char+": \tmedian = "+str(aiStats.letterPlaysInvCDF(char, .5)-groupMedian)
	print "\tmean = "+str(aiStats.letterPlaysMean(char)-groupMean)
	print "\t25th percentile: "+str(aiStats.letterPlaysInvCDF(char, .25)-group25p)
	print "\t75th percentile: "+str(aiStats.letterPlaysInvCDF(char, .75)-group75p)
	print "\tStd dev: "+str(aiStats.letterPlaysStdDev(char)/groupStdDev)
	print "\tBest play ever: "+str(aiStats.getHighestWord(char))
	
	print "\nHighest-ever word score: "+str(aiStats.getHighestWord())
	print str(len(aiStats.letterPlays['Q']))+" games played counting letter statistics.\n"
	
	print "Latest Heuristic Game Analysis:"
	print "Test won "+str(100.0*aiStats.getGamesWon() / (len(aiStats.scores) + 0.00001))+"% of games."
	print "Mean performance improvement: "+str(aiStats.getGameDiffMean())
	print "Performance difference stddev: "+str(aiStats.getGameDiffStdDev())
	
	
	print str(len(aiStats.scores))+" games played in this round of testing.\n"
	
	#for i in range(0, 20, 1):
	#	print str(100*aiStats.timingCDF(i)) + '% would be completed successfully in '+ str(i) +' seconds'
		
	
	'''while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		
		pygame.display.update()	'''