from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_todos():
    if not os.path.exists("todos.json"):
        return []
    with open("todos.json", "r") as f:
        return json.load(f)

def save_todos(todos):
    with open("todos.json", "w") as f:
        json.dump(todos, f, ensure_ascii=False)

def check_deadline(deadline):
    if not deadline:
        return ""
    today = datetime.today().date()
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
    diff = (deadline_date - today).days
    if diff < 0:
        return "overdue"
    elif diff <= 3:
        return "near"
    return ""

@app.route("/")
def index():
    todos = load_todos()
    query = request.args.get("query", "")  # 検索キーワードを受け取る
    for todo in todos:
        todo["deadline_status"] = check_deadline(todo.get("deadline"))
    if query:
        todos = [t for t in todos if query in t["title"]]  # タイトルで絞り込む
    active = [t for t in todos if not t["done"]]
    done = [t for t in todos if t["done"]]
    return render_template("index.html", active=active, done=done, query=query)

@app.route("/add", methods=["POST"])
def add():
    todos = load_todos()
    title = request.form.get("title")
    deadline = request.form.get("deadline")
    priority = request.form.get("priority")
    if title:
        todo = {
            "id": len(todos) + 1,
            "title": title,
            "deadline": deadline,
            "priority": priority,
            "done": False
        }
        todos.append(todo)
        save_todos(todos)
    return redirect("/")

@app.route("/edit/<int:todo_id>")
def edit(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            return render_template("edit.html", todo=todo)
    return redirect("/")

@app.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["title"] = request.form.get("title")
            todo["deadline"] = request.form.get("deadline")
            todo["priority"] = request.form.get("priority")
    save_todos(todos)
    return redirect("/")

@app.route("/complete/<int:todo_id>")
def complete(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
    save_todos(todos)
    return redirect("/")

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)