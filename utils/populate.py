import os
import sqlite3
import random
with open("users.txt", "r") as f:
    ids = list(map(int, f))
urls = [(f"https://{A}.douban.com/people/{B}/collect?mode=list",) for A in ["book", "movie"] for B in ids]
random.shuffle(urls)
if os.path.exists("spider.db"):
    os.remove("spider.db")
db = sqlite3.connect("spider.db")
db.execute("CREATE TABLE state (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, value INTEGER)")
db.execute("INSERT INTO state (key, value) VALUES ('next', 0)")
db.execute("CREATE TABLE urls (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL UNIQUE)")
db.execute("CREATE TABLE records (id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER NOT NULL, item INTEGER NOT NULL, rating INTEGER NOT NULL)")
db.executemany("INSERT INTO urls (url) VALUES (?)", urls)
db.commit()
db.close()
