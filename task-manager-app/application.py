from flask import Flask, render_template, request, redirect
import pymysql
import boto3
import json
import os

application = Flask(__name__)


def get_secret():
    secret_name = os.environ.get("SECRET_NAME", "task-manager-db-secret")
    region_name = os.environ.get("AWS_REGION", "ap-south-1")

    client = boto3.client("secretsmanager", region_name=region_name)

    response = client.get_secret_value(SecretId=secret_name)

    secret = json.loads(response['SecretString'])
    return secret


def connection():
    secret = get_secret()

    return pymysql.connect(
        host=secret['host'],
        user=secret['username'],
        password=secret['password'],
        database=secret['dbname'],
        port=int(secret['port']),
        cursorclass=pymysql.cursors.DictCursor
    )


@application.route("/", methods=["GET", "POST"])
def index():
    conn = connection()
    cursor = conn.cursor()

    if request.method == "POST":
        task = request.form["task"]
        cursor.execute("INSERT INTO tasks(task_name) VALUES(%s)", (task,))
        conn.commit()

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", tasks=tasks)


@application.route("/delete/<int:id>")
def delete_task(id):
    conn = connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/")


@application.route("/complete/<int:id>")
def complete_task(id):
    conn = connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET status='Completed' WHERE id=%s", (id,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/")
