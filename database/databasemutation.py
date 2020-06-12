import sqlite3

conn = sqlite3.connect('userdb.sqlite3')
cur = conn.cursor()
cur.execute('''
SELECT * FROM discordGuardiansToken;
''')
print(cur.fetchall())