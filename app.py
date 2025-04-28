from dotenv import load_dotenv
import os
import sys
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from engine import SuperChatbot  # ваш реальный движок чата

# Загрузка переменных из .env
load_dotenv()

# Инициализация Flask
app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
app.secret_key = os.getenv('SECRET_KEY')

# Настройки для базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'superfitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки для Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true') == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Инициализация расширений
db = SQLAlchemy(app)
mail = Mail(app)

# Подключение чатбота
chatbot = SuperChatbot()

# Модель для регистрации студентов
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    time_of_day = db.Column(db.String(20), nullable=False)
    session_length = db.Column(db.String(20), nullable=False)

# Создание базы данных (если не существует)
with app.app_context():
    db.create_all()

# Роут для главной страницы
@app.route("/")
def home():
    return render_template("home.html")

# Роут для страницы расписания
@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        student_email = request.form.get("student_email")
        day_of_week = request.form.get("day_of_week")
        time_of_day = request.form.get("time_of_day")
        session_length = request.form.get("session_length")

        # Проверяем количество записей на слот
        count = Registration.query.filter_by(
            day_of_week=day_of_week,
            time_of_day=time_of_day
        ).count()

        if count >= 3:
            flash(f"Sorry, the {day_of_week} {time_of_day} slot is already full.", "danger")
        else:
            # Записываем в базу данных
            new_registration = Registration(
                student_name=student_name,
                student_email=student_email,
                day_of_week=day_of_week,
                time_of_day=time_of_day,
                session_length=session_length
            )
            db.session.add(new_registration)
            db.session.commit()

            # Попытка отправить email
            try:
                # Проверка: если приложение не на Render Free, отправляем email
                if not os.getenv('RENDER_EXTERNAL_HOSTNAME'):
                    msg = Message(
                        subject="Super Fitness Club Registration Confirmation",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[student_email],
                        body=f"Hi {student_name},\n\nYou are registered for {day_of_week} at {time_of_day} ({session_length}).\n\nSee you in class!\n\n- Super Fitness Club Team"
                    )
                    mail.send(msg)
                    flash("Successfully registered and confirmation email sent.", "success")
                else:
                    # Если мы на Render Free, пропускаем отправку email
                    flash("Successfully registered (email sending skipped on Render Free plan).", "success")
            except Exception as e:
                flash(f"Registered but failed to send confirmation email: {str(e)}", "warning")

        return redirect(url_for('schedule'))

    return render_template("schedule.html")


# Страница профиля тренера
@app.route("/trainer")
def trainer_profile():
    return render_template("trainer_profile.html")

# Страница инструктора
@app.route("/instructor")
def instructor():
    return render_template("instructor.html")

# Страница виртуального класса
@app.route("/virtual-class")
def virtual_class():
    return render_template("virtual_class.html")

# Страница логина
@app.route("/login")
def login():
    return render_template("login.html")

# Страница чатбота
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_page():
    response = ""
    if request.method == "POST":
        user_question = request.form.get("question", "")
        if user_question.strip():
            response = chatbot.answer_question(user_question)
        else:
            response = "Please ask a question."
    return render_template("chatbot_page.html", response=response)

# Запуск приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
