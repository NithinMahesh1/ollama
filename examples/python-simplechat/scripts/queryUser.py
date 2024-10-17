import sqlite3

con = sqlite3.connect("/Documents/MyGit/ollama/examples/python-simplechat/db/chat.db")

cur = con.cursor()

rows = cur.execute("Select * from User")

for row in rows:
    print(row)