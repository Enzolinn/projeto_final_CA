from flask import Flask, abort, jsonify, request
from tinydb import Query, TinyDB
from tinydb.operations import set as tiny_set
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
db = TinyDB("db.json")
todos_table = db.table("todos")
Todo = Query()


def format_doc(doc):
    """Retorna um dict com 'id' exposto (doc_id do TinyDB)."""
    result = dict(doc)
    result["id"] = doc.doc_id
    return result


@app.route("/todos", methods=["GET"])
def list_todos():
    docs = todos_table.all()

    return jsonify([format_doc(d) for d in docs]), 200


@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    doc = todos_table.get(doc_id=todo_id)
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify(format_doc(doc)), 200


@app.route("/todos", methods=["POST"])
def create_todo():
    try:
        payload = request.get_json(force=True)
    except BadRequest:
        return jsonify({"error": "JSON inválido"}), 400

    title = payload.get("title")
    if not title or not isinstance(title, str):
        return jsonify({"error": "Campo 'title' obrigatório (string)"}), 400

    done = bool(payload.get("done", False))
    doc_id = todos_table.insert({"title": title, "done": done})
    doc = todos_table.get(doc_id=doc_id)
    return jsonify(format_doc(doc)), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    doc = todos_table.get(doc_id=todo_id)
    if not doc:
        return jsonify({"error": "Not found"}), 404

    try:
        payload = request.get_json(force=True)
    except BadRequest:
        return jsonify({"error": "JSON inválido"}), 400

    updates = {}
    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"]:
            return jsonify({"error": "Campo 'title' precisa ser string não vazia"}), 400
        updates["title"] = payload["title"]
    if "done" in payload:
        updates["done"] = bool(payload["done"])

    if updates:
        todos_table.update(updates, doc_ids=[todo_id])

    doc = todos_table.get(doc_id=todo_id)
    return jsonify(format_doc(doc)), 200


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    doc = todos_table.get(doc_id=todo_id)
    if not doc:
        return jsonify({"error": "Not found"}), 404
    todos_table.remove(doc_ids=[todo_id])
    return jsonify({"message": "Deleted"}), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "message": "API TODO simples",
            "endpoints": {
                "GET /todos": "lista todos",
                "GET /todos/<id>": "detalha",
                "POST /todos": {"title": "string", "done": "boolean (opcional)"},
                "PUT /todos/<id>": "atualiza title/done",
                "DELETE /todos/<id>": "remove",
            },
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
