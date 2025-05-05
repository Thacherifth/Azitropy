from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import qrcode
import os
import pandas as pd
from collections import Counter

app = Flask(__name__)
app.secret_key = 'secret_key'

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
    {
        "id": 3,
        "question": "Quelle est la période d'incubation moyenne du VIH ?",
        "choices": ["Quelques jours", "1-2 semaines", "2-4 semaines", "1 an"],
        "answer": 2,
        "explanation": "L'incubation du VIH est généralement de 2 à 4 semaines."
    },
    {
        "id": 4,
        "question": "Quel vaccin est recommandé contre l’hépatite B ?",
        "choices": ["BCG", "DTPolio", "Engerix-B", "ROR"],
        "answer": 2,
        "explanation": "Le vaccin Engerix-B est recommandé contre l’hépatite B."
    },
    {
        "id": 5,
        "question": "Quelle est la bactérie la plus souvent responsable de la pneumonie ?",
        "choices": ["S. aureus", "H. influenzae", "S. pneumoniae", "M. tuberculosis"],
        "answer": 2,
        "explanation": "Streptococcus pneumoniae est l’agent pathogène le plus fréquent de la pneumonie."
    },
    {
        "id": 6,
        "question": "Quel est le vecteur du virus Zika ?",
        "choices": ["Tique", "Moustique Aedes", "Chien", "Rat"],
        "answer": 1,
        "explanation": "Le virus Zika est transmis principalement par les moustiques Aedes."
    },
    {
        "id": 7,
        "question": "Quelle infection est souvent nosocomiale ?",
        "choices": ["Grippe", "E. coli urinaire", "Rougeole", "Varicelle"],
        "answer": 1,
        "explanation": "Les infections urinaires à E. coli sont fréquemment nosocomiales."
    },
    {
        "id": 8,
        "question": "Quel test rapide détecte la streptocoque A ?",
        "choices": ["CRP", "Test de Mantoux", "TROD", "IDR"],
        "answer": 2,
        "explanation": "Les TROD (Tests Rapides d’Orientation Diagnostique) détectent la streptocoque A."
    }
]


@app.route("/")
def home():
    return render_template("index.html", questions=questions)


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"status": "error", "message": "Nom requis."}), 400

    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", "results.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if name in df["name"].values:
            return jsonify({"status": "error", "message": "Vous avez déjà participé."}), 403

    save_results(data)
    return jsonify({"status": "ok"})


def save_results(data):
    file_path = os.path.join("data", "results.csv")
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame([data])
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)


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

    file_path = os.path.join("data", "results.csv")
    if not os.path.exists(file_path):
        return render_template("stats.html", stats=[])

    df = pd.read_csv(file_path)
    stats = []

    for q in questions:
        answers = df.get(f'q{q["id"]}').dropna() if f'q{q["id"]}' in df else []
        counts = dict(Counter(answers))
        details = df[["name", f"q{q['id']}"]].dropna().to_dict(orient="records") if f'q{q["id"]}' in df else []
        stats.append({
            "question": q["question"],
            "choices": q["choices"],
            "counts": counts,
            "correct": q["answer"],
            "explanation": q["explanation"],
            "details": details
        })

    return render_template("stats.html", stats=stats)


@app.route("/generate_qr")
def generate_qr():
    url = "https://quiz-infectieux.onrender.com"
    qr = qrcode.make(url)
    os.makedirs("static", exist_ok=True)
    qr.save("static/qr.png")
    return "QR code généré."


if __name__ == "__main__":
    app.run(debug=True)
