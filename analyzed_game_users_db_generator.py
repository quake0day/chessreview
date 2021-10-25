import sqlite3
con = sqlite3.connect('analyzed_game_users.db')
cur = con.cursor()
cur.execute("CREATE TABLE users (user text, isProcessing text)")
con.commit()
con.close()
