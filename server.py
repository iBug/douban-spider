import os
import threading
import MySQLdb
from flask import *


db_pool = {}


def connect_db():
    try:
        return db_pool[threading.get_ident()]
    except KeyError:
        conn = MySQLdb.connect("localhost", "spider", "spider", "spider")
        db_pool[threading.get_ident()] = conn
        return conn


app = Flask(__name__)
job_id = 0


@app.route("/get-jobs", methods=["GET"])
def get_jobs():
    global job_id
    try:
        c = connect_db().cursor()
        job_count = 5
        rows = c.execute("SELECT id, user, type, page FROM jobs WHERE id > %s AND completed = 0 AND invalid = 0 LIMIT %s", [job_id, job_count])
        if not rows:
            c.fetchall()
            job_id = 0
            rows = c.execute("SELECT id, user, type, page FROM jobs WHERE id > %s AND completed = 0 AND invalid = 0 LIMIT %s", [job_id, job_count])
            if not rows:
                # No more jobs
                raise ValueError("No more jobs available")
        result = c.fetchall()
        job_id = max([i[0] for i in result])
        return jsonify([{'id': s, 'user': a, 'type': b, 'page': c} for s, a, b, c in result])
    finally:
        c.close()


@app.route("/add-result", methods=["POST"])
def add_result():
    global job_id
    try:
        db = connect_db()
        c = db.cursor()
        data = request.json
        if data['type'] not in [0, 1]:
            return "", 400
        name = ["books", "movies"][data['type']]
        c.execute("UPDATE jobs SET completed = 0 WHERE id = %s", [data['id']])
        c.execute(f"UPDATE users SET {name} = %s WHERE id = %s", [data['total'], data['user']])
        db.commit()
        return jsonify({}), 200
    finally:
        c.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
