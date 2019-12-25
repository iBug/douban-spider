#!/usr/bin/python3

import os
import sqlite3
from flask import Flask, request, jsonify


DB_FILE = "spider.db"
nextId = 0


if not os.path.exists(DB_FILE):
    raise FileNotFoundError(f"{DB_FILE} expected")
app = Flask(__name__)


def connect_db():
    return sqlite3.connect(DB_FILE)


@app.route("/get_job", methods=["GET", "POST"])
def get_job():
    global nextId
    try:
        db = connect_db()
        cursor = db.execute("SELECT id, url FROM urls WHERE id > ? ORDER BY id ASC LIMIT 5", [nextId])
        records = cursor.fetchall()
        # No records?
        if not records:
            # Reached end of array, restart from beginning
            cursor = db.execute("SELECT id, url FROM urls ORDER BY id ASC LIMIT 5")
            records = cursor.fetchall()
            if records is None:
                # We've run out of available URLs
                return jsonify(None)
        nextId = max([a for a, b in records])
        urls = [b for a, b in records]
        return jsonify(urls)
    finally:
        db.close()


@app.route("/complete_job", methods=["POST"])
def complete_job():
    data = request.get_json()
    # Assert the following key exists:
    #   oldUrl: the URL for the job
    #   newUrl: the "next page" link, None if last page
    #   items: any rating results crawled
    oldUrl = data["oldUrl"]
    newUrl = data["newUrl"]
    items = [(x["user"], x["item"], x["rating"]) for x in data["items"]]
    try:
        db = connect_db()
        if not newUrl:
            # newUrl is None, this record is over
            db.execute("DELETE FROM urls WHERE url = ?", [oldUrl])
        else:
            db.execute("UPDATE urls SET url = ? WHERE url = ?", [newUrl, oldUrl])
        db.executemany("INSERT INTO records (user, item, rating) VALUES (?, ?, ?)", items)
        db.commit()
    finally:
        db.close()
    return jsonify({})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
