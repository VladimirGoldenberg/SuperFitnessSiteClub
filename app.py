from dotenv import load_dotenv
import os
import sys

load_dotenv()
from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
from engine import SuperChatbot  # <-- Connect to real backend

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# DEBUG: Print environment values to stderr (будут видны в Render logs)
print("\n====== EMAIL CONFIG DEBUG ======", file=sys.stderr)
print("MAIL_SERVER:", os.getenv('MAIL_SERVER'), file=sys.stderr)
print("MAIL_PORT:", os.getenv('MAIL_PORT'), file=sys.stderr)
print("MAIL_USE_TLS:", os.getenv('MAIL_USE_TLS'), file=sys.stderr)
print("MAIL_USERNAME:", os.getenv('MAIL_USERNAME'), file=sys.stderr)
print("MAIL_PASSWORD SET:", bool(os.getenv('MAIL_PASSWORD')), file=sys.stderr)
print("================================\n", file=sys.stderr)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 587)  # fallback на 587
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true') == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

# Load chatbot once at app startup
chatbot = SuperChatbot()

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_page():
    response = ""
    if request.method == "POST":
        user_question = request.form.get("question", "")
        if user_question.strip():
            response = chatbot.answer_question(user_question)
        else:
            response = "Please ask a question."
    return render_template("chatbot.html", response=response)

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        user_input = request.form.get("question", "")
        if user_input.strip():
            response = chatbot.answer_question(user_input)
        else:
            response = "Please ask a question."
    return render_template("index.html", response=response)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/virtual-class")
def virtual_class():
    return render_template("virtual_class.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")

@app.route("/instructor")
def instructor():
    return render_template("instructor.html")

@app.route("/trainer")
def trainer_profile():
    return render_template("trainer_profile.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    class_info = request.form.get("class_info")

    print(f"[DEBUG] Preparing to send email to {email}...", file=sys.stderr)

    if not all([app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']]):
        print("[ERROR] Missing mail configuration.", file=sys.stderr)
        flash("Email configuration incomplete. Please contact admin.", "danger")
        return redirect("/schedule")

    try:
        msg = Message(
            subject="Class Signup Confirmation",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"Hi {name},\n\nYou've signed up for:\n{class_info}\n\nSee you in class!"
        )
        mail.send(msg)
        print("[DEBUG] Email sent successfully.", file=sys.stderr)
        flash("Confirmation email sent successfully.", "success")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}", file=sys.stderr)
        flash(f"Failed to send confirmation: {str(e)}", "danger")

    return redirect("/schedule")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
