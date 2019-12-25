#!/usr/bin/python3

import os
import sqlite3
from flask import Flask, request, jsonify


DB_FILE = "spider.db"


if not os.path.exists(DB_FILE):
    raise FileNotFoundError(f"{DB_FILE} expected")
app = Flask(__name__)


def connect_db():
    return sqlite3.connect(DB_FILE)


@app.route("/get_url")
def get_url():
    try:
        db = connect_db()
        cursor = db.execute("SELECT url FROM urls LIMIT 1")
        url = cursor.fetchone()
        db.execute("DELETE FROM urls WHERE url = ?", url)
        db.commit()
        return jsonify(url[0])
    finally:
        db.close()


@app.route("/add_url", methods=["POST"])
def add_url():
    data = request.get_json()
    if "url" in data:
        try:
            db = connect_db()
            cursor = db.execute("INSERT INTO urls (url) VALUES (?)", [data["url"]])
            db.commit()
        finally:
            db.close()
    return jsonify({})


@app.route("/add_records", methods=["POST"])
def add_records():
    data = request.get_json()
    items = [(x["user"], x["item"], x["rating"]) for x in data]
    try:
        db = connect_db()
        cursor = db.executemany("INSERT INTO records (user, item, rating) VALUES (?, ?, ?)", items)
        db.commit()
    finally:
        db.close()
    return jsonify({})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
