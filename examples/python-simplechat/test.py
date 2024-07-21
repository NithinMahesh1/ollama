import os
import sqlite3

conn = sqlite3.connect("/Users/nithinmahesh/Documents/MyGit/OllamaTesting/temp/chat.db")

arr = ["test","tester","testing","tested", "nithin"]
cursor = conn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS TEST(id INTEGER PRIMARY KEY, content TEXT)')

i=0
for item in arr:
    cursor.execute('INSERT INTO TEST VALUES (?,?)',(i,item))
    i += 1

conn.commit()

print("Input Table: ")
cursor.execute('SELECT * FROM TEST')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()

# cursor.execute('CREATE TABLE input(id INTEGER PRIMARY KEY, model TEXT,message TEXT,date_created DEFAULT CURRENT_TIMESTAMP,lineObj TEXT)')