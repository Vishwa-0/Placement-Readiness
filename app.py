from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np

app = Flask(__name__)

with open("PRS.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    if request.method == "POST":
        data = [
            int(request.form["dsa"]),
            int(request.form["problems"]),
            int(request.form["projects"]),
            int(request.form["github"]),
            int(request.form["domain"])
        ]
        prediction = model.predict([data])[0]
        confidence = model.predict_proba([data])[0][prediction]

        return redirect(url_for(
            "dashboard",
            ready=prediction,
            confidence=round(confidence * 100, 2),
            level=data[0]
        ))

    return render_template("assessment.html")

@app.route("/dashboard")
def dashboard():
    ready = request.args.get("ready")
    confidence = request.args.get("confidence")
    level = int(request.args.get("level"))

    if level <= 2:
        projects = ["Portfolio Website", "To-Do App", "Basic ML Classifier"]
    elif level == 3:
        projects = ["Job Portal", "REST API App", "ML Recommendation System"]
    else:
        projects = ["Scalable Web App", "ML Pipeline", "Cloud Microservices"]

    return render_template(
        "dashboard.html",
        ready=ready,
        confidence=confidence,
        projects=projects
    )

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
