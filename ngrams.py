'''
This file is for processing Google's n-gram data to fill a dictionary 
with relative word frequencies.

The file is parsed, and if a match is made it is added to the count.
Periodically the scrabblewords-ngram.txt is saved and updated with
a number representing total usage count in English.
'''

import sys, dictionarywords

class NGramReader:
	
	def __init__(self, filename, dictFilename):
		self.filename = filename
		self.dictionary = dictionarywords.DictionaryWords(dictFilename)
		
	def parse(self):
		
		lineNumber = 0
		lastWord = ""
		totalUsage = 0
		wordsUpdated = 0
		
		with open(self.filename) as infile:
			for line in infile:
				
				line = line.rstrip()
				tokens = line.split()
				
				word = tokens[0].split("_")[0]
				count = int(tokens[2])
				
				if lastWord == word:
					totalUsage += count
				else:
					isScrabbleWord = self.dictionary.setUsage(lastWord, totalUsage)
					totalUsage = count
					
					if isScrabbleWord:
						wordsUpdated += 1
				
				
				lastWord = word
				
				
				lineNumber += 1
				if lineNumber % 10000000 == 0:
					print str(wordsUpdated)+" words added to dictionary."
					self.dictionary.saveUsage("media/scrabblewords_usage.txt")
					
					
		self.dictionary.saveUsage("media/scrabblewords_usage.txt")
					
		
		
if __name__ == "__main__":
	
	ngrams = NGramReader("ngrams/googlebooks-eng-all-1gram-20120701-z", "media/scrabblewords_usage.txt")
	#ngrams.dictionary.saveUsage("media/scrabblewords_usage.txt")
	ngrams.parse()