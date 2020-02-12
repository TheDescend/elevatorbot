from database               import getMarkovPairs
import random

def getMarkovSentence(startword = '__start__'):
    markovpairs = getMarkovPairs()
    nextwordlist = [b for (a,b) in markovpairs if a == startword]
    #print('nw:', nextwordlist)
    if len(nextwordlist) == 0:
        return 'I don\'t know that word :('
    
    sentencelist = []
    while len(sentencelist) < 4:
        nextword = random.choice([b for (a,b) in markovpairs if a == startword and b != '__end__'])
        sentencelist = []
        while nextword != '__end__':
            sentencelist.append(nextword)
            try:
                nextword = random.choice([b for (a,b) in markovpairs if a.lower() == sentencelist[-1].lower()])
            except IndexError:
                sentencelist.append('*ERROR*')
                nextword = '__end__'
            if len(sentencelist) > 25:
                break
    mtext = ' '.join(sentencelist)

    if random.randint(0,10) == 10:
        mtext = mtext[::-1]
    return mtext
