import sqlite3

conn = sqlite3.connect('telega.db')
cur = conn.cursor()
cur.execute('delete from tickets')
conn.commit()
conn.close()