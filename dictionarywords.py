'''
Words class creates a new word list object which can allow for fast
data access of words
'''

import board, time, math

class DictionaryWords:
	
	'''
	Loads the list of valid words. 
	'''
	def __init__(self, filename):
		self.words = {}
		self.lookupTime = 0
		dictFile = open(filename, 'r')
		for line in dictFile:
			line = line.rstrip()
			tokens = line.split()
			if len(tokens) == 1:
				count = -1
			elif len(tokens) == 2:
				count = int(tokens[1])
				
			self.words[tokens[0]] = count
			
	'''
	Checks if the word is in the dictionary
	'''
	def isValid(self, word, vocabulary = -1):
		
	
		if board.Board.DEBUG_ERRORS:
			startTime = time.time()
	
		#True if the word was in the dictionary
		if self.words.has_key(word):
			value = self.words[word]
			success = True
			if vocabulary > 0:
				
				#give all words a default "1" usage
				if value <= 0:
					value = 1
					
				if value < vocabulary:
					success = False
		
		else:
			success = False
		
		
					
		if board.Board.DEBUG_ERRORS:
			timeSpent = time.time()-startTime
			self.lookupTime += timeSpent
		
		return success
		
	'''
	Match with blanks returns a list of all blank assignments that
	correspond to real words
	'''		
	def matchWithBlanks(self, word, vocabulary = -1, assignment=[]):
		
		#BASE CASE: all blanks have been filled
		if not ' ' in word:
			if self.isValid(word, vocabulary):
				return [assignment]
			else:
				return []
		else:
			i = word.find(' ')
			blankAssignments = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				if i == 0:
					newWord = char + word[1:]
				elif i == len(word)-1:
					newWord = word[:-1] + char
				else:
					newWord = word[:i] + char + word[i+1:]
				
				newAssignment = assignment[:]
				newAssignment.append(char)
				results = self.matchWithBlanks(newWord, vocabulary, newAssignment)
				for result in results:
					blankAssignments.append(result)
							
			return blankAssignments
						
						
	'''
	Sets the count of the word in the dictionary
	'''					
	def setUsage(self, word, usage):
		word = word.upper()
		word = word.rstrip()
		if self.isValid(word):
			self.words[word] = usage
			return True
		else:
			return False
			
	'''
	Saves the dictionary with usage values as well
	'''		
	def saveUsage(self, filename):
		with open(filename, 'w') as outfile:
			keylist = self.words.keys()
			keylist.sort()
			for w in keylist:	
				outfile.write(w+"\t"+str(self.words[w])+"\n")	
			
	'''
	Resets the lookup time so we can determine time only for querying the hashtable
	'''	
	def resetLookupTime(self):
		self.lookupTime = 0
		
		
	'''
	From a difficulty ranking between 1 (easiest) and 10 (hardest) this will return
	a usage value for vocabulary checking
	'''
	def difficultyToUsage(self, difficulty):
		alpha = 10 - (difficulty/10.0)*6.5
		usage = math.exp(alpha)
		
		#Max difficulty has complete vocabulary
		if difficulty >= 9.999:
			usage = -1
			
		return usage
		
		
#TEST		
if __name__ == '__main__':	
	dic = DictionaryWords("media/scrabblewords_usage.txt")
	usages = []
	for i in range(10):
		usages.append( dic.difficultyToUsage(i+1) )
		
	word = "PORK"
	print word+": "+str(dic.words[word])	
	i = 0
	for usage in usages:
		i += 1
		if not dic.isValid(word, usage):
			suffix = "n't"
		else:
			suffix = ""
		print "Difficulty level "+str(i)+" could"+suffix+" play this. "+str(usage)	