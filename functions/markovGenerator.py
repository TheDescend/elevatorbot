from functions.database               import getMarkovPairs
import random

def getMarkovSentence(startword = '__start__'):
    markovpairs = getMarkovPairs()
    startwordlist = [b for (a,b) in markovpairs if a == startword and b != '__end__'] 
    #print('nw:', nextwordlist)
    if len(startwordlist) == 0:
        return 'I don\'t know that word :('
    
    sentencelist = []
    while len(sentencelist) < 4:
        nextword = random.choice([b for (a,b) in markovpairs if a == startword and b != '__end__'])
        sentencelist = []
        while nextword != '__end__':
            sentencelist.append(nextword)
            nextword = random.choice([b for (a,b) in markovpairs if a.lower() == sentencelist[-1].lower()])
            if len(sentencelist) > 25:
                break
    mtext = ' '.join(sentencelist)

    if random.randint(0,100) == 69:
        mtext = f'**__{mtext[::-1]}__**'
    return mtext
