from flask import Flask, render_template, request, redirect, url_for, session
import pickle

app = Flask(__name__)
app.secret_key = "vynox-secret-key"

with open("PRS.pkl", "rb") as f:
    model = pickle.load(f)

def get_recommendations(level):
    if level <= 2:
        return {
            "projects": [
                "Portfolio Website",
                "To-Do App with Auth",
                "Basic Python Automation",
                "Simple ML Classifier",
                "Blog Website"
            ],
            "skills": ["Python Basics", "HTML/CSS", "Git", "Problem Solving"]
        }
    elif level == 3:
        return {
            "projects": [
                "Job Portal Web App",
                "REST API with Flask",
                "Recommendation System",
                "Dashboard Application",
                "Mini SaaS Project"
            ],
            "skills": ["DSA Intermediate", "APIs", "Databases", "System Basics"]
        }
    else:
        return {
            "projects": [
                "Scalable Web Platform",
                "ML Pipeline Project",
                "Cloud Deployed App",
                "Microservices System",
                "Real-world SaaS Clone"
            ],
            "skills": ["System Design", "Cloud", "Advanced DSA", "DevOps"]
        }

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

        prediction = int(model.predict([data])[0])
        confidence = round(model.predict_proba([data])[0][prediction] * 100, 2)

        session["assessed"] = True
        session["level"] = data[0]
        session["ready"] = prediction
        session["confidence"] = confidence

        return redirect(url_for("results"))

    return render_template("assessment.html")

@app.route("/results")
def results():
    if not session.get("assessed"):
        return redirect(url_for("assessment"))

    rec = get_recommendations(session["level"])

    return render_template(
        "results.html",
        ready=session["ready"],
        confidence=session["confidence"],
        projects=rec["projects"],
        skills=rec["skills"]
    )

@app.route("/dashboard")
def dashboard():
    if not session.get("assessed"):
        return redirect(url_for("assessment"))

    return render_template(
        "dashboard.html",
        ready=session["ready"],
        confidence=session["confidence"]
    )

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
