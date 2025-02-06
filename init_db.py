import sqlite3
import env

conn = sqlite3.connect(env.DATABASE_NAME)
cur  = conn.cursor()


cur.execute(
    "CREATE TABLE pages(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, url STRING, img STRING, latest STRING, favorite INTEGER, updated DATE)"
)
conn.commit()
conn.close()

