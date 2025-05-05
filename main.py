from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
from collections import Counter

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ✅ MODEL DE BASE DE DONNÉES
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)
    q5 = db.Column(db.Integer)
    q6 = db.Column(db.Integer)
    q7 = db.Column(db.Integer)
    q8 = db.Column(db.Integer)

# ✅ QUESTIONS DU QUIZ
questions = [
    {
        "id": 1,
        "question": "Quel est l'agent infectieux du paludisme ?",
        "choices": ["Virus", "Bactérie", "Parasite", "Champignon"],
        "answer": 2,
        "explanation": "Le paludisme est causé par un parasite du genre Plasmodium transmis par les moustiques."
    },
    {
        "id": 2,
        "question": "La tuberculose est causée par ?",
        "choices": ["E. coli", "Mycobacterium tuberculosis", "Streptocoque", "Salmonelle"],
        "answer": 1,
        "explanation": "La tuberculose est causée par la bactérie Mycobacterium tuberculosis."
    },
    # More questions...
]

# Initialize DB before the first request
@app.before_request
def create_db():
    os.makedirs("data", exist_ok=True)
    db.create_all()

# Your other routes and functions here...

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/")
def home():
    return render_template("index.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"status": "error", "message": "Nom requis."}), 400

    if Submission.query.filter_by(name=name).first():
        return jsonify({"status": "error", "message": "Vous avez déjà participé."}), 403

    submission = Submission(name=name)
    for q in questions:
        question_key = f"q{q['id']}"
        setattr(submission, question_key, data.get(question_key))

    db.session.add(submission)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/admin_stats", methods=["GET", "POST"])
def admin_stats():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "achour123":
            session["authenticated"] = True
            return redirect(url_for("admin_stats"))
        else:
            return render_template("access_denied.html"), 403

    if not session.get("authenticated"):
        return render_template("admin_login.html")

    submissions = Submission.query.all()
    stats = []

    for q in questions:
        answer_column = f"q{q['id']}"
        counts = Counter(getattr(s, answer_column) for s in submissions if getattr(s, answer_column) is not None)
        details = [{
            "name": s.name,
            "answer_index": getattr(s, answer_column)
        } for s in submissions if getattr(s, answer_column) is not None]

        stats.append({
            "question": q["question"],
            "choices": q["choices"],
            "counts": dict(counts),
            "correct": q["answer"],
            "explanation": q["explanation"],
            "details": details
        })

    return render_template("stats.html", stats=stats)

def generate_qr():
    url = "https://azitropy.onrender.com"
    qr = qrcode.make(url)
    os.makedirs("static", exist_ok=True)
    qr.save("static/qr.png")

if __name__ == "__main__":
    generate_qr()
    app.run(debug=True)
