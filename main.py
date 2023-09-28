import hashlib
import datetime

from flask import Flask, render_template, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import redirect

from for_work_with_database import db_session
from for_work_with_database.class_db_competition import Competition
from for_work_with_database.class_db_team import TeamDB

from for_work_with_database.class_db_user import User

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from forms.LoginForm import LoginForm
from forms.NewCompetition import NewCompetition
from forms.RegTeamForm import TeamForm

import json

from flask_ngrok import run_with_ngrok

with open(".\data\const_data.json", "r", encoding="utf-8") as file:
    file_contents = file.read()
    const_data_json = json.loads(file_contents)
app = Flask(__name__)
run_with_ngrok(app)

app.secret_key = "roboExtreme"
limiter = Limiter(get_remote_address, app=app)

login_manager = LoginManager()

login_manager.init_app(app)


# Страница которая говорит о том что пользователь не имеет возможности создания соревнования
# потому что у него нет роли "Администратор"
@app.route("/message_about_that_you_are_not_a_administration")
@limiter.limit("5/second")
def message_about_that_you_are_not_a_administration():
    return render_template("message_about_that_you_are_not_a_administration.html")


# Создание нового соревнования
@app.route("/create_new_competition", methods=["POST", "GET"])
@limiter.limit("5/second")
def create_new_competition():
    if current_user.is_authenticated:
        if request.method == "POST":

            db_sess = db_session.create_session()

            new_competition = Competition()
            new_competition.date = request.form["date_of_start_competition"]
            new_competition.date_of_ending_registration_members = request.form["date_of_ending_registration_members"]
            new_competition.commentary = request.form["commentary_for_competition"]
            new_competition.date_of_startig_registration_members = request.form["date_of_starting_registration_members"]
            new_competition.started = "not_started"
            new_competition.header_for_competition = request.form["header_for_competition"]

            db_sess.add(new_competition)
            db_sess.commit()

            return redirect("/")

        elif request.method == "GET":
            return render_template("new_competition.html", form=NewCompetition())

    else:
        return redirect("/message_about_that_you_are_not_a_administration")




# Главная страница сайта
@app.route("/")
@limiter.limit("5/second")
def main_page():
    sess = db_session.create_session()
    competitions = sorted(sess.query(Competition).all(), key=lambda x: x.date)

    return render_template("main_page.html", competitions=competitions)


# Авторизация аккаунта пользователя в программе и определение current_user
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()

    return db_sess.query(User).get(user_id)


# Выход пользователя из аккаунта в программе, и удаление current_user
@app.route('/logout')
@limiter.limit("5/second")
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect("/")

    logout_user()

    return redirect("/")


# Хэширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Поставить соревнованию статус закончено или же началот
@app.route("/to_end_this_competition/<string:end_or_start>/<int:id>", methods=["GET"])
@limiter.limit("5/second")
def to_end_this_competition(end_or_start, id):
    if not current_user.is_authenticated:
        return redirect("/")

    if end_or_start != "ended" and end_or_start != "started":
        return redirect("/")

    sess = db_session.create_session()
    competition = sess.query(Competition).filter(Competition.id == id).first()
    competition.started = end_or_start
    sess.commit()
    sess.close()

    return redirect("/")

# Авторизация пользователя
@app.route("/login_user", methods=["GET", "POST"])
@limiter.limit("5/second")
def login():
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form["email"]).first()

        if user and user.check_password(hash_password(request.form["password"])):
            login_user(user)

            return redirect("/")

        return render_template('login_user.html',
                               message="Неправильный логин или пароль",
                               form=LoginForm())

    elif request.method == "GET":
        return render_template("login_user.html", form=LoginForm())


# Определение id номинации в базе данных по названию(принимает только такие значения: "pilot", "autopilot") и возвращает только 1 или 2
def find_nominatation_id_by_name(name_of_nomination):
    if name_of_nomination == "pilot":
        return 1

    return 2


# Перевод из id(в базе данных) номинации в строку для пользователя которую покажут на странице
def find_nominatation_name_by_id(name_of_nomination):
    if name_of_nomination == 1:
        return "Пилот"

    return "Автопилот"


# Перевод из id(в базе данных) номинации в строку на английском для пользователя которую покажут на странице
def find_english_nominatation_name_by_id(name_of_nomination):
    if name_of_nomination == 1:
        return "pilot"

    return "autopilot"


# Ифнормация для судьи об соревновании которое он судит
@app.route("/information_about_competition/<int:competition_id>/<string:nomination>/<int:number_of_launch>")
@limiter.limit("5/second")
def information_about_competition(competition_id, nomination, number_of_launch):
    if not current_user.is_authenticated:
        return redirect("/")

    sess = db_session.create_session()
    teams = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id)
    competition = sess.query(Competition).filter(Competition.id == competition_id).first()
    return render_template("page_about_competition.html",
                           teams=list(teams),
                           len=len,
                           competition=competition,
                           number_of_launch=number_of_launch,
                           competition_id=competition_id,
                           nomination=nomination)

# @app.route("/timer/<int:competition_id>/<string:nomination>/<int:number_of_launch>/<int:id_team>", methods=["POST"])
# @limiter.limit("5/second")
# def to_end_this_competition_POST(end_or_start, id):
#     for i in request.form:
#         print(i, "-", request.form[i])
#     return redirect("/")
# Страница дя судейства соревнования
@app.route("/timer/<int:competition_id>/<string:nomination>/<int:number_of_launch>/<int:id_team>", methods=["GET", "POST"])
@limiter.limit("5/second")
def timer(competition_id, nomination, number_of_launch, id_team):
    if not current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        """
            ***Здесь будут считаться баллы
        """
        return redirect(f"/timer/{competition_id}/{nomination}/{number_of_launch}/{id_team}")

    if request.method == "GET":
        sess = db_session.create_session()
        teams = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id).all()
        team = sess.query(TeamDB).filter(TeamDB.id == id_team).first()
        print(team.name_command, 1)

        return render_template("timer.html",
                               affected_persons=const_data_json["list_of_affected"],
                               len=len,
                               team=team,
                               teams=teams,
                               nomination=nomination,
                               numb=0,
                               competition_id=competition_id, number_of_launch=number_of_launch)


# Админ может отредактировать команду в таблице
@app.route("/redact_team/<int:team_id>", methods=["POST", "GET"])
@limiter.limit("5/second")
def to_redact_this_team_by_admin(team_id):
    if current_user.is_authenticated:

        if current_user.role_id == 2:
            return redirect("/")

    else:
        return redirect("/")

    sess = db_session.create_session()
    current_team = sess.query(TeamDB).filter(TeamDB.id == team_id).first()

    if request.method == "GET":
        form = TeamForm(
            name_command=current_team.name_command,
            name_of_organization=current_team.name_of_organization,
            manager=current_team.manager,
            number_phone_of_manager=current_team.number_phone_of_manager,
            email_of_manager=current_team.email_of_manager,
            name_first_member=current_team.name_first_member,
            last_name_first_member=current_team.last_name_first_member,
            middle_name_first_member=current_team.middle_name_first_member,
            date_birthday_first_member=current_team.date_birthday_first_member,
            certificate_PFDO_first_member=current_team.certificate_PFDO_first_member,
            name_second_member=current_team.name_second_member,
            middle_name_second_member=current_team.middle_name_second_member,
            last_name_second_member=current_team.last_name_second_member,
            date_birthday_second_member=current_team.date_birthday_second_member,
            certificate_PFDO_second_member=current_team.certificate_PFDO_second_member
        )
        nom = find_nominatation_name_by_id(current_team.nomination)
        print(nom)
        print(current_team.nomination)
        return render_template("registration_new_team.html", create_or_redact_team_form_html="redact", form=form, nom=nom)

    elif request.method == "POST":
        current_team.name_command = request.form["name_command"]
        current_team.name_of_organization = request.form["name_of_organization"]
        current_team.manager = request.form["manager"]
        current_team.number_phone_of_manager = request.form["number_phone_of_manager"]
        current_team.email_of_manager = request.form["email_of_manager"]
        current_team.name_first_member = request.form["name_first_member"]
        current_team.last_name_first_member = request.form["last_name_first_member"]
        current_team.middle_name_first_member = request.form["middle_name_first_member"]
        current_team.date_birthday_first_member = request.form["date_birthday_first_member"]
        current_team.certificate_PFDO_first_member = request.form["certificate_PFDO_first_member"]
        current_team.name_second_member = request.form["name_second_member"]
        current_team.middle_name_second_member = request.form["middle_name_second_member"]
        current_team.last_name_second_member = request.form["last_name_second_member"]
        current_team.date_birthday_second_member = request.form["date_birthday_second_member"]
        current_team.certificate_PFDO_second_member = request.form["certificate_PFDO_second_member"]
        current_team.nomination = request.form["nomination"]
        competition_id = current_team.competition_id
        sess.commit()
        sess.close()

        return redirect(f"/table/{find_english_nominatation_name_by_id(request.form['nomination'])}/{competition_id}")


# Демонстрация таблиц "Итог", "Жеребьёвка", "Зарегистрированные"
@app.route("/table/<string:nomination_name>/<int:id>")
@limiter.limit("5/second")
def show_table(nomination_name, id):
    """
        ***Дать возможность админам изменять всё кроме баллов
    """
    nomination_id = find_nominatation_id_by_name(nomination_name)
    sess = db_session.create_session()
    print(TeamDB.competition_id)
    members = sess.query(TeamDB).filter(TeamDB.nomination == nomination_id, TeamDB.competition_id == id)
    print(members)
    competition = sess.query(Competition).filter(Competition.id == id).first()

    string_date, string_time = competition.date_of_ending_registration_members.split("T")
    string_time = string_time.split(":")
    string_date = string_date.split("-")

    close_of_registration = datetime.datetime(day=int(string_date[2]), month=int(string_date[1]),
                                              year=int(string_date[0]), hour=int(string_time[0]),
                                              minute=int(string_time[1]))
    nomination_name_for_table_head = find_nominatation_name_by_id(nomination_id)
    now_datetime = datetime.datetime.now()

    if now_datetime > close_of_registration:
        members_random_queue = sorted(members, key=lambda x: x.random_queue)
        final_members_of_competition = sorted(members, key=lambda x: x.final_top)
        started_of_competition = True

        return render_template("show_table_of_competition.html", nomination=nomination_id, members=members,
                               competition=competition, final_members_of_competition=final_members_of_competition,
                               members_random_queue=members_random_queue, started_of_competition=started_of_competition,
                               nomination_show=nomination_name_for_table_head)

    started_of_competition = False
    sess.close()

    return render_template("show_table_of_competition.html", nomination=nomination_id, members=members,
                           competition=competition, started_of_competition=started_of_competition,
                           nomination_show=nomination_name_for_table_head)


# Регистрация команды на соревнование по id соревнования
@app.route("/reg_team/<int:id>", methods=["GET", "POST"])
@limiter.limit("5/second")
def reg_team(id):
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        team = TeamDB()

        team.certificate_PFDO_first_member = request.form["certificate_PFDO_first_member"]
        team.certificate_PFDO_second_member = request.form["certificate_PFDO_second_member"]
        team.last_name_second_member = request.form["last_name_second_member"]
        team.name_second_member = request.form["name_second_member"]
        team.middle_name_second_member = request.form["middle_name_second_member"]
        team.nomination = request.form["nomination"]
        team.date_birthday_second_member = request.form["date_birthday_second_member"]
        team.name_command = request.form["name_command"]
        team.name_of_organization = request.form["name_of_organization"]
        team.competition_id = id
        team.manager = request.form["manager"]
        team.number_phone_of_manager = request.form["number_phone_of_manager"]
        team.email_of_manager = request.form["email_of_manager"]
        team.name_first_member = request.form["name_first_member"]
        team.last_name_first_member = request.form["last_name_first_member"]
        team.middle_name_first_member = request.form["middle_name_first_member"]
        team.date_birthday_first_member = request.form["date_birthday_first_member"]
        team.final_top = -1
        team.final_score = 0
        team.fisrt_score = ("0, " * 10)[:-2]
        team.second_score = ("0, " * 10)[:-2]
        team.team_id = team.id
        team.nomination = request.form["nomination"]

        db_sess = db_session.create_session()
        db_sess.add(team)
        db_sess.commit()

        return redirect("/")

    elif request.method == "GET":
        return render_template("registration_new_team.html", form=TeamForm(), create_or_redact_team_form_html="create")


print("http://127.0.0.1:5000/timer")
print("http://127.0.0.1:5000/timer/4/pilot/1/6")
print("http://127.0.0.1:5000/information_about_competition/4/pilot")
if __name__ == "__main__":
    db_session.global_init("dataBase/database.db")
    app.run()
