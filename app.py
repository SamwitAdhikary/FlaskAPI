import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get("/")
def home():
    return "Hello World"

CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, firstname TEXT, lastname TEXT, job TEXT);"

with connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_USERS_TABLE)

@app.route("/api/user/", methods=["POST"])
def create_user():
    data = request.get_json()
    firstname = data["firstname"]
    lastname = data["lastname"]
    job = data["job"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (firstname, lastname, job) VALUES (%s, %s, %s) RETURNING id;", (firstname, lastname, job))
            user_id = cursor.fetchone()[0]
    return {"id": user_id, "firstname": firstname, "lastname": lastname, "job": job, "message": f"User {firstname} {lastname} created."}, 201

@app.route("/api/user/", methods=["GET"])
def get_all_users():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            if users:
                result = []
                for user in users:
                    result.append({"id": user[0], "firstname": user[1], "lastname": user[2], "job": user[3]})
                return jsonify(result)
            else:
                return jsonify({"error": f"Users not found"}), 404
            
@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({"id": user[0], "firstname": user[1], "lastname": user[2], "job": user[3]})
            else:
                return jsonify({"error": f"User with ID {user_id} not found."})
            
@app.route("/api/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    firstname = data["firstname"]
    lastname = data["lastname"]
    job = data["job"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET firstname = %s, lastname = %s, job = %s WHERE id = %s", (firstname, lastname, job, user_id))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {user_id} not found."}), 404
    return jsonify({"id": user_id, "firstname": firstname, "lastname": lastname, "job": job, "message": f"User with ID {user_id} updated."})

@app.route("/api/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": f"User with ID {user_id} not found."})
    return jsonify({"message": f"User with ID {user_id} deleted."})

