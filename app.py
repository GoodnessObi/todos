from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ""
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship("Todo", backref="list", lazy=True)


def __repr__(self):
    return f"<TodoList {self.id} {self.name}>"


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey("todolists.id"), nullable=False)

    def __repr__(self):
        return f"<Todo {self.id} {self.description}>"


@app.route("/lists/create", methods=["POST"])
def create_todolist():
    error = False
    body = {}
    try:
        name = request.get_json()["name"]
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body["id"] = todolist.id
        # body['completed'] = todo.completed
        body["name"] = todolist.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)


@app.route("/lists/<list_id>/set-completed", methods=["POST"])
def set_completed_list(list_id):
    try:
        completed = request.get_json()["completed"]
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            todo.completed = True
        list.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/lists/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)

        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        # redirect(url_for('index'))
    return jsonify({"success": True})


@app.route("/todos/create", methods=["POST"])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()["description"]
        list_id = request.get_json()["listId"]
        todo = Todo(description=description, list_id=list_id, completed=False)
        db.session.add(todo)
        db.session.commit()
        body["id"] = todo.id
        body["listId"] = todo.list_id
        body["completed"] = todo.completed
        body["description"] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)


@app.route("/todos/<todo_id>/set-completed", methods=["POST"])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()["completed"]
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/todos/<todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        # todo = Todo.query.get(todo_id)
        # db.session.delete(todo)
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        # redirect(url_for('index'))
    return jsonify({"success": True})


@app.route("/lists/<list_id>")
def get_list_todos(list_id):
    # render_template
    return render_template(
        "index.html",
        lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query.filter_by(list_id=list_id).order_by("id").all(),
    )


@app.route("/")
def index():
    return redirect(url_for("get_list_todos", list_id=1))
