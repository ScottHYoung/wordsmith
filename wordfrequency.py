'''
This class stores in a file the count of the words used
by all players in all games. It can load and update the
word frequency file wordfreq.txt
'''

import dictionarywords, math

class WordFrequency:
	
	FILENAME = "media/wordfreq.txt"
	DICTIONARY = "media/scrabblewords_usage.txt"
	
	def __init__(self):
		
		self.count = {}
		self.load()
		self.dict = dictionarywords.DictionaryWords(WordFrequency.DICTIONARY)
		
	def load(self):
		try:
			freqFile = open(WordFrequency.FILENAME, 'r')
		
			for line in freqFile:
				tokens = line.split()
				assert len(tokens) == 2
				word = tokens[0]
				freq = int(tokens[1])
			
				self.count[word] = freq
		except IOError as e:
			pass
			
	def save(self):
		
		freqFile = open(WordFrequency.FILENAME, 'w')
		
		for word in self.count.keys():
			freqFile.write(word+" "+str(self.count[word])+"\n")
			
	def wordPlayed(self, word):
		if self.count.has_key(word):
			self.count[word] += 1
		else:
			self.count[word] = 1
			
	def displayStats(self):
		
		totalPlayed = 0
		playedOnlyOnce = 0
		longest = 0
		longestWord = ""
		numberSevenLetters = 0
		threeLetters = {}
		fourLetters = {}
		fiveLetters = {}
		wordsWithQ = {}
		wordsWithX = {}
		wordsWithZ = {}
		wordsWithJ = {}
		wordsWithK = {}
		wordsWithY = {}
		wordsWithV = {}
		wordsWithF = {}
		wordsWithW = {}
		wordsWithC = {}
		for word in self.count.keys():
			totalPlayed += self.count[word]
			if len(word) > longest:
				longest = len(word)
				longestWord = word
			if len(word) >= 7:
				numberSevenLetters += 1
			if self.count[word] == 1:
				playedOnlyOnce += 1	
			if len(word) == 3:
				threeLetters[word] = self.count[word]
			elif len(word) == 4:
				fourLetters[word] = self.count[word]
			elif len(word) == 5:
				fiveLetters[word] = self.count[word]
			
			if 'Q' in word:
				wordsWithQ[word] = self.count[word]
			if 'Z' in word:
				wordsWithZ[word] = self.count[word]				
			if 'J' in word:
				wordsWithJ[word] = self.count[word]
			if 'X' in word:
				wordsWithX[word] = self.count[word]		
			if 'K' in word:
				wordsWithK[word] = self.count[word]		
			if 'Y' in word:
				wordsWithY[word] = self.count[word]
			if 'V' in word:
				wordsWithV[word] = self.count[word]	
			if 'F' in word:
				wordsWithF[word] = self.count[word]	
			if 'W' in word:
				wordsWithW[word] = self.count[word]
			if 'C' in word:
				wordsWithC[word] = self.count[word]	
				
				
		
		print "Unique words = " + str(len(self.count.keys()))
		print "Words played = " + str(totalPlayed)
		print "Words played only once = " + str(playedOnlyOnce)
		print "Longest word played: "+longestWord
		print "Number of words at least seven letters long: "+str(numberSevenLetters)
		
		print "Top 500 Most Frequent Words: "
		i = 1
		for w in sorted(self.count, key=self.count.get, reverse=True):
			self.printFreq(i, w, self.count[w])
			i += 1
			if i > 500:
				break
		print ""		
				
		print "Top 10 Most Frequent 3-Letter Words: "
		i = 1
		for w in sorted(threeLetters, key=threeLetters.get, reverse=True):
			self.printFreq(i, w, threeLetters[w])
			i += 1
			if i > 10:
				break	
		print ""
				
		print "Top 10 Most Frequent 4-Letter Words: "
		i = 1
		for w in sorted(fourLetters, key=fourLetters.get, reverse=True):
			self.printFreq(i, w, fourLetters[w])
			i += 1
			if i > 10:
				break	
		print ""
		
		print "Top 10 Most Frequent 5-Letter Words: "
		i = 1
		for w in sorted(fiveLetters, key=fiveLetters.get, reverse=True):
			self.printFreq(i, w, fiveLetters[w])
			i += 1
			if i > 10:
				break	
		print ""		
		
		print "Top 10 Most Common Words with 'Q'"						
		i = 1
		for w in sorted(wordsWithQ, key=wordsWithQ.get, reverse=True):
			self.printFreq(i, w, wordsWithQ[w])
			i += 1
			if i > 10:
				break	
		print ""						

		print "Top 10 Most Common Words with 'Z'"						
		i = 1
		for w in sorted(wordsWithZ, key=wordsWithZ.get, reverse=True):
			self.printFreq(i, w, wordsWithZ[w])
			i += 1
			if i > 10:
				break	
		print ""

		print "Top 10 Most Common Words with 'J'"						
		i = 1
		for w in sorted(wordsWithJ, key=wordsWithJ.get, reverse=True):
			self.printFreq(i, w, wordsWithJ[w])
			i += 1
			if i > 10:
				break	
		print ""	
		
		print "Top 10 Most Common Words with 'X'"						
		i = 1
		for w in sorted(wordsWithX, key=wordsWithX.get, reverse=True):
			self.printFreq(i, w, wordsWithX[w])
			i += 1
			if i > 10:
				break	
		print ""
		
		print "Top 10 Most Common Words with 'K'"						
		i = 1
		for w in sorted(wordsWithK, key=wordsWithK.get, reverse=True):
			self.printFreq(i, w, wordsWithK[w])
			i += 1
			if i > 10:
				break	
		print ""
		
		print "Top 10 Most Common Words with 'Y'"						
		i = 1
		for w in sorted(wordsWithY, key=wordsWithY.get, reverse=True):
			self.printFreq(i, w, wordsWithY[w])
			i += 1
			if i > 10:
				break	
		print ""		
		
		print "Top 10 Most Common Words with 'V'"						
		i = 1
		for w in sorted(wordsWithV, key=wordsWithV.get, reverse=True):
			self.printFreq(i, w, wordsWithV[w])
			i += 1
			if i > 10:
				break	
		print ""							
		
 		print "Top 10 Most Common Words with 'F'"						
		i = 1
		for w in sorted(wordsWithF, key=wordsWithF.get, reverse=True):
			self.printFreq(i, w, wordsWithF[w])
			i += 1
			if i > 10:
				break	
		print ""	

 		print "Top 10 Most Common Words with 'W'"						
		i = 1
		for w in sorted(wordsWithW, key=wordsWithW.get, reverse=True):
			self.printFreq(i, w, wordsWithW[w])
			i += 1
			if i > 10:
				break	
		print ""
		
 		print "Top 10 Most Common Words with 'C'"						
		i = 1
		for w in sorted(wordsWithC, key=wordsWithC.get, reverse=True):
			self.printFreq(i, w, wordsWithC[w])
			i += 1
			if i > 10:
				break	
		print ""			
		
	def printFreq(self, i, w, count):
		difficulty = int(((10-math.log(self.dict.words[w]))/6.5)*10.0)
		print str(i) + ")\t" + w + "\t\tused "+str(count)+" times. At difficulty level: "+str(difficulty)			
			


#RUNNING WORD FREQUENCY ON ITS OWN PROVIDES STATISTICS			
if __name__ == '__main__':
	wordfreq = WordFrequency()
	wordfreq.displayStats()
				
		