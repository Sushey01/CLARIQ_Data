from flask import Flask, request, jsonify
from flask_cors import CORS
from .session_manager import SessionManager

app = Flask(__name__)
CORS(app)
manager = SessionManager()


@app.route("/api/session/init", methods=["POST"])
def init_session():
    data = request.get_json() or {}
    student_id = data.get("student_id", "anonymous")
    session = manager.create_session(student_id)
    return jsonify(
        {
            "session_id": session["session_id"],
            "studentLevel": session["studentLevel"],
            "preferredStrategy": session["preferredStrategy"],
            "profile": session["profile"],
        }
    )


if __name__ == "__main__":
    # Run a simple dev server: python -m src.rag.session_api
    app.run(host="0.0.0.0", port=8000, debug=True)
