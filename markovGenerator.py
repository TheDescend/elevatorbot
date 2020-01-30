from database               import getMarkovPairs
import random

def getMarkovSentence():
    markovpairs = getMarkovPairs()
    nextword = random.choice([b for (a,b) in markovpairs if a == '__start__'])
    
    sentencelist = []
    while nextword != '__end__':
        sentencelist.append(nextword)
        nextword = random.choice([b for (a,b) in markovpairs if a.lower() == sentencelist[-1].lower()])
    return(' '.join(sentencelist))
