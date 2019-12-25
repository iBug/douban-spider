#!/usr/bin/python3

import os
import sqlite3
import threading
from flask import Flask, jsonify


DB_FILE = "spider.db"


if not os.path.exists(DB_FILE):
    raise FileNotFoundError(f"{DB_FILE} expected")
db = sqlite3.connect(DB_FILE)
db_lock = threading.Lock()
app = Flask(__name__)


@app.route("/get_url")
def get_url():
    try:
        db_lock.acquire()
        cursor = db.execute("SELECT url FROM urls LIMIT 1")
        url = cursor.fetchone()
        db.execute("DELETE FROM urls WHERE url = ?", [url])
        db.commit()
        return jsonify(url)
    finally:
        db_lock.release()


@app.route("/add_url", methods=["POST"])
def add_url():
    data = request.get_json()
    if "url" in data:
        try:
            db_lock.acquire()
            cursor = db.execute("INSERT INTO urls (url) VALUES (?)", [data["url"]])
            db.commit()
        finally:
            db_lock.release()
    return jsonify({})


@app.route("/add_records", methods=["POST"])
def add_records():
    data = request.get_json()
    items = [(x["user"], x["item"], x["rating"]) for x in data]
    try:
        db_lock.acquire()
        cursor = db.executemany("INSERT INTO records (user, item, rating) VALUES (?, ?, ?)", items)
        db.commit()
    finally:
        db_lock.release()
    return jsonify({})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
