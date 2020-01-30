from events.base_event      import BaseEvent

from database               import db_connect
from markovGenerator        import getMarkovSentence


class AutomaticRoleAssignment(BaseEvent):

    def __init__(self):
        interval_minutes = 2880  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        conn = db_connect()
        c = conn.cursor()
        c.execute('''DELETE FROM markovpairs''')#TRUNCATE
        conn.commit()
        c.execute('''
        SELECT msg FROM messagedb
        ''')
        text = list(c.fetchall())
        for dbquery in text:
            sentence = dbquery[0]
            words = sentence.split(' ')
            sentenceedges = zip(['__start__'] + words, words + ['__end__'])
            for (a,b) in sentenceedges:
                    conn.execute(f'''
                    INSERT INTO markovpairs 
                    (word1, word2) 
                    VALUES 
                    (?,?)
                    ''',(a,b))
        conn.commit()

        client.get_channel(670400011519000616).send(getMarkovSentence())
