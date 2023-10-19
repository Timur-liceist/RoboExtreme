import hashlib
import datetime

from flask import Flask, render_template, request, url_for
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

import logging
import os

import json

import random

# from flask_ngrok import run_with_ngrok

with open("./data/const_data.json", "r", encoding="utf-8") as file:
    file_contents = file.read()
    const_data_json = json.loads(file_contents)
app = Flask(__name__)
# run_with_ngrok(app)

app.secret_key = "roboExtreme"
limiter = Limiter(get_remote_address, app=app)

REQUESTS_TIME = "5/second"

login_manager = LoginManager()

login_manager.init_app(app)


def create_file_handler(competition_id):
    log_folder = 'logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_filename = os.path.join(log_folder, f'competition_{competition_id}.log')
    file_handler = logging.FileHandler(log_filename)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    return file_handler


def log_to_competition(competition_id, message):
    logger = logging.getLogger(f'competition_{competition_id}')
    logger.setLevel(logging.INFO)

    file_handler = create_file_handler(competition_id)

    logger.addHandler(file_handler)
    logger.info(message)
    logger.removeHandler(file_handler)


# Страница которая говорит о том что пользователь не имеет возможности создания соревнования
# потому что у него нет роли "Администратор"
@app.route("/message_about_that_you_are_not_a_administration")
@limiter.limit(REQUESTS_TIME)
def message_about_that_you_are_not_a_administration():
    return render_template("message_about_that_you_are_not_a_administration.html")


# Создание нового соревнования
@app.route("/create_new_competition", methods=["POST", "GET"])
@limiter.limit(REQUESTS_TIME)
def create_new_competition():
    if current_user.is_authenticated:
        if request.method == "POST":

            db_sess = db_session.create_session()

            new_competition = Competition()
            new_competition.date = request.form["date_of_start_competition"]
            new_competition.date_of_ending_registration_members = request.form["date_of_ending_registration_members"]
            new_competition.commentary = request.form["commentary_for_competition"]
            new_competition.date_of_starting_registration_members = request.form[
                "date_of_starting_registration_members"]
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
@limiter.limit(REQUESTS_TIME)
def main_page():
    sess = db_session.create_session()
    competitions = sorted(sess.query(Competition).all(), key=lambda x: x.date, reverse=True)
    now_datetime = datetime.datetime.now()
    return render_template("main_page.html", competitions=competitions, strptime=datetime.datetime.strptime, now_datetime=now_datetime)


# Авторизация аккаунта пользователя в программе и определение current_user
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()

    return db_sess.query(User).get(user_id)


# Выход пользователя из аккаунта в программе, и удаление current_user
@app.route('/logout')
@limiter.limit(REQUESTS_TIME)
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect("/")

    logout_user()

    return redirect("/")


# Хэширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_random_array(n):
    numbers = list(range(1, n + 1))

    random.shuffle(numbers)

    return numbers

@app.route("/to_redact_score_and_time_of_race/<int:team_id>/<int:number_of_launch>", methods=["GET", "POST"])
@limiter.limit(REQUESTS_TIME)
def to_redact_score_and_time_of_race(team_id, number_of_launch):
    print(request.method)
    if not current_user.is_authenticated:
        return redirect("/")

    if current_user.role_id == 1:
        return redirect("/")

    sess = db_session.create_session()
    team = sess.query(TeamDB).filter(TeamDB.id == team_id).first()

    if request.method == "GET":

        affected_persons = const_data_json["list_of_affected"]

        if number_of_launch == 2:
            time_of_race = team.time_of_second_race
            try:
                list_logs_score = team.list_logs_score_of_second_race.split(", ")
            except AttributeError:
                list_logs_score = []

        elif number_of_launch == 1:
            time_of_race = team.time_of_first_race
            try:
                list_logs_score = team.list_logs_score_of_first_race.split(", ")
            except AttributeError:
                list_logs_score = []
        try:
            seconds = time_of_race % 60
            minutes = time_of_race // 60
        except TypeError:
            minutes = 5
            seconds= 30
        return render_template("to_redact_score_and_time.html", list_logs_score=list_logs_score,
                               team=team, affected_persons=affected_persons, minutes=minutes, seconds=seconds, number_of_launch=number_of_launch, str=str)

    elif request.method == "POST":
        for key in request.form:
            print(key)
        score_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        time_of_launch = 0
        list_logs_score = []

        for key in request.form:

            if key == "score_start":
                list_logs_score.append(key)
                score_list[0] += 3

            elif key == "minutes":

                time_of_launch += int(request.form[key]) * 60

            elif key == "seconds":
                time_of_launch += int(request.form[key])

            else:
                list_logs_score.append(key)
                key = list(map(int, key.split("_")))
                score_list[key[0]] += key[1] * const_data_json["affected_and_score"][
                    const_data_json["list_of_affected"][key[0]]]

        if number_of_launch == 1:
            team.list_logs_score_of_first_race = ", ".join(list_logs_score)
            team.first_score = ", ".join(list(map(str, score_list)))
            team.final_score = sum(list(map(int, team.second_score.split(", ")))) + sum(score_list)

            team.time_of_first_race = time_of_launch

            sess.commit()

        elif number_of_launch == 2:
            team.list_logs_score_of_first_race = ", ".join(list_logs_score)
            team.second_score = ", ".join(list(map(str, score_list)))
            team.final_score = sum(list(map(int, team.first_score.split(", ")))) + sum(score_list)

            team.time_of_second_race = time_of_launch

            sess.commit()


        return redirect(f"/table/{find_english_nominatation_name_by_id(team.nomination)}/{team.competition_id}")




# Поставить соревнованию статус закончено или же началот
@app.route("/to_end_this_competition/<string:end_or_start>/<int:competition_id>", methods=["GET"])
@limiter.limit(REQUESTS_TIME)
def to_end_this_competition(end_or_start, competition_id):
    if not current_user.is_authenticated:
        return redirect("/")

    if end_or_start != "ended" and end_or_start != "started":
        return redirect("/")

    sess = db_session.create_session()
    competition = sess.query(Competition).filter(Competition.id == competition_id).first()

    competition.started = end_or_start

    sess.commit()

    if end_or_start == "started":
        teams_from_pilot = sess.query(TeamDB).filter(TeamDB.competition_id==competition_id, TeamDB.nomination==1).all()
        indexes_randomy_list = generate_random_array(len(teams_from_pilot))

        for index_of_current_team in range(len(teams_from_pilot)):
            teams_from_pilot[index_of_current_team].random_queue = indexes_randomy_list[index_of_current_team]

        sess.commit()

        teams_from_autopilot = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id, TeamDB.nomination == 2).all()
        indexes_randomy_list = generate_random_array(len(teams_from_autopilot))

        for index_of_current_team in range(len(teams_from_autopilot)):
            teams_from_autopilot[index_of_current_team].random_queue = indexes_randomy_list[index_of_current_team]

        sess.commit()



    elif end_or_start == "ended":
        teams = sess.query(TeamDB).filter(TeamDB.competition_id)
        place_on_sompetition = 1

        for current_team in sorted(teams, key=lambda x: x.final_score, reverse=True):
            current_team.final_top = place_on_sompetition
            place_on_sompetition += 1

        sess.commit()

    sess.close()

    return redirect("/")


# Авторизация пользователя
@app.route("/login_user", methods=["GET", "POST"])
@limiter.limit(REQUESTS_TIME)
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


@app.route("/redact_random_queue/<int:competition_id>/<string:nomination>", methods=["POST", "GET"])
@limiter.limit(REQUESTS_TIME)
def redact_random_queue(competition_id, nomination):
    if not current_user.is_authenticated:
        return redirect("/")

    if current_user.role_id == 1:
        return redirect("/")

    sess = db_session.create_session()
    print(find_nominatation_id_by_name(nomination), type(find_nominatation_id_by_name(nomination)))
    teams = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id, TeamDB.nomination == find_nominatation_id_by_name(nomination)).all()
    for i in teams:
        print(i.nomination)
    if request.method == "GET":
        return render_template("redact_random_queue.html", teams=teams, is_error=False, competition_id=competition_id,
                               nomination_show=find_nominatation_name_by_id(find_nominatation_id_by_name(nomination)))

    elif request.method == "POST":
        set_of_id_teams = set()  # Множество для проверки на опечатку на повтор номеров порядковых
        message = None
        for current_team in teams:
            try:
                value_from_form = int(request.form[str(current_team.id)])
            except ValueError:
                message = f"Невозможный порядковый номер у команды '{current_team.name_command}'"
                break
            current_team.random_queue = value_from_form

            if value_from_form in set_of_id_teams:
                message = f"Порядковый номер у команды '{current_team.name_command}' совпадает с порядковым номером другой команды"
                break

            elif value_from_form > len(request.form) or value_from_form <= 0:
                message = f"Невозможный порядковый номер у команды '{current_team.name_command}'"
                break

            else:
                current_team.random_queue = value_from_form
                set_of_id_teams.add(value_from_form)

        else:
            print("Commit!")
            sess.commit()
            return redirect("/")
        return render_template("redact_random_queue.html", str=str, teams=teams, message=message, is_error=True, dict_of_last_values=request.form, competition_id=competition_id,
                               nomination_show=find_nominatation_name_by_id(find_nominatation_id_by_name(nomination)))


# Ифнормация для судьи об соревновании которое он судит
@app.route("/information_about_competition/<int:competition_id>/<string:nomination>/<int:number_of_launch>")
@limiter.limit(REQUESTS_TIME)
def information_about_competition(competition_id, nomination, number_of_launch):
    if not current_user.is_authenticated:
        return redirect("/")

    sess = db_session.create_session()
    teams = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id).all()
    competition = sess.query(Competition).filter(Competition.id == competition_id).first()

    teams.sort(key=lambda x: x.random_queue)

    return render_template("page_about_competition.html",
                           teams=list(teams),
                           len=len,
                           competition=competition,
                           number_of_launch=number_of_launch,
                           competition_id=competition_id,
                           nomination=nomination)


def translate_name_of_affectred_from_rus_to_literate(name_of_affected):
    dict_for_translate = {'Аслан': 'Aslan',
                          'Батраз': 'Batraz',
                          'Вахтанг': 'Vakhtang',
                          'Георгий': 'Georgiy',
                          'Хетаг': 'KHetag',
                          'Заур': 'Zaur',
                          'Маир': 'Mair',
                          'Турмец': 'Turmets',
                          'Инал': 'Inal',
                          'Давид': 'David'
                          }

    return dict_for_translate[name_of_affected]


# Страница для судейства соревнования
@app.route("/timer/<int:competition_id>/<string:nomination>/<int:number_of_launch>/<string:id_team>",
           methods=["GET", "POST"])
@limiter.limit(REQUESTS_TIME)
def timer(competition_id, nomination, number_of_launch, id_team):
    id_team = int(id_team)
    if not current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        score_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        sess = db_session.create_session()
        teams = sess.query(TeamDB).filter(  TeamDB.competition_id == competition_id).all()
        team = sess.query(TeamDB).filter(TeamDB.id == id_team).first()
        time_of_launch = None
        list_logs_score = []
        for key in request.form:
            if key == "score_start":
                list_logs_score.append(key)
                score_list[0] += 3
                log_to_competition(competition_id,
                                   f"score=3 for start from zone A"
                                   f" for team '{team.name_command}' "
                                   f"with id={id_team} at nomination '{nomination}'")
            elif key == "time_of_launch":
                time_of_launch = int(request.form[key])
            else:
                list_logs_score.append(key)
                key = list(map(int, key.split("_")))
                score_list[key[0]] += key[1] * const_data_json["affected_and_score"][
                    const_data_json["list_of_affected"][key[0]]]

                log_to_competition(competition_id,
                                   f"score={key[1]}"
                                   f"(with coefficient"
                                   f" = {key[1] * const_data_json['affected_and_score'][const_data_json['list_of_affected'][key[0]]]}) "
                                   f"for affected '{translate_name_of_affectred_from_rus_to_literate(const_data_json['list_of_affected'][key[0]])}'"
                                   f" for team '{team.name_command}' "
                                   f"with id={id_team} at nomination '{nomination}'")

        if number_of_launch == 1:
            log_to_competition(competition_id, f"team '{team.name_command}' finished the first race"
                                               f" with a score = {sum(score_list)} "
                                               f"and time of race {time_of_launch}")

        elif number_of_launch == 2:
            log_to_competition(competition_id, f"team '{team.name_command}' finished the second race with "
                                               f"a score = {sum(score_list)} "
                                               f"and time of race {time_of_launch} sec")

        if number_of_launch == 1:
            team.list_logs_score_of_first_race = ", ".join(list_logs_score)
            team.first_score = ", ".join(list(map(str, score_list)))
            team.final_score = sum(list(map(int, team.second_score.split(", ")))) + sum(score_list)

            team.time_of_first_race = time_of_launch

            sess.commit()

        elif number_of_launch == 2:
            team.list_logs_score_of_first_race = ", ".join(list_logs_score)
            team.second_score = ", ".join(list(map(str, score_list)))
            team.final_score = sum(list(map(int, team.first_score.split(", ")))) + sum(score_list)

            team.time_of_second_race = time_of_launch

            sess.commit()

        for current_team in range(len(teams)):
            if teams[current_team] == team:
                if current_team == len(teams) - 1:
                    if number_of_launch == 2:
                        next_id_team = -1
                    elif number_of_launch == 1:
                        next_id_team = teams[0].id
                        number_of_launch = 2
                else:
                    next_id_team = teams[current_team + 1].id
        print(number_of_launch)
        return redirect(f"/timer/{competition_id}/{nomination}/{number_of_launch}/{next_id_team}")

    if request.method == "GET":

        if id_team == -1:
            return redirect(f"/information_about_competition/{competition_id}/{nomination}/1")

        sess = db_session.create_session()
        teams = sess.query(TeamDB).filter(TeamDB.competition_id == competition_id).all()
        team = sess.query(TeamDB).filter(TeamDB.id == id_team).first()

        teams.sort(key=lambda x: x.random_queue)

        return render_template("timer.html",
                               affected_persons=const_data_json["list_of_affected"],
                               len=len,
                               team=team,
                               teams=teams,
                               nomination=nomination,
                               numb=0,
                               url_for=url_for,
                               str=str,
                               competition_id=competition_id, number_of_launch=number_of_launch)


# Админ может отредактировать команду в таблице
@app.route("/redact_team/<int:team_id>", methods=["POST", "GET"])
@limiter.limit(REQUESTS_TIME)
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

        return render_template("registration_new_team.html", create_or_redact_team_form_html="redact", form=form,
                               nom=nom)

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
@limiter.limit(REQUESTS_TIME)
def show_table(nomination_name, id):
    nomination_id = find_nominatation_id_by_name(nomination_name)
    sess = db_session.create_session()

    members = sess.query(TeamDB).filter(TeamDB.nomination == nomination_id, TeamDB.competition_id == id)

    competition = sess.query(Competition).filter(Competition.id == id).first()

    competition_date = list(map(int, competition.date.split("-")))

    close_of_registration = datetime.date(month=competition_date[1], year=competition_date[0], day=competition_date[2])
    nomination_name_for_table_head = find_nominatation_name_by_id(nomination_id)
    now_datetime = datetime.date.today()

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
@app.route("/reg_team/<int:competition_id>", methods=["GET", "POST"])
@limiter.limit(REQUESTS_TIME)
def reg_team(competition_id):
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        db_sess = db_session.create_session()
        team = TeamDB()
        now_datetime = datetime.datetime.now()
        competition = db_sess.query(Competition).filter(Competition.id == competition_id).first()
        if datetime.datetime.strptime(competition.date_of_ending_registration_members,
                                      "%Y-%m-%dT%H:%M") > now_datetime and datetime.datetime.strptime(
            competition.date_of_starting_registration_members, "%Y-%m-%dT%H:%M") < now_datetime:
            pass
        else:
            return render_template("error_about_datetime_of_later_registration.html")

        if request.form["is_second_member"] == "True":
            team.last_name_second_member = request.form["last_name_second_member"]
            team.certificate_PFDO_second_member = request.form["certificate_PFDO_second_member"]
            team.name_second_member = request.form["name_second_member"]
            team.middle_name_second_member = request.form["middle_name_second_member"]
            team.date_birthday_second_member = request.form["date_birthday_second_member"]
        else:
            team.last_name_second_member = "-"
            team.certificate_PFDO_second_member = "-"
            team.name_second_member = "-"
            team.middle_name_second_member = "-"
            team.date_birthday_second_member = "-"
        team.certificate_PFDO_first_member = request.form["certificate_PFDO_first_member"]
        team.nomination = request.form["nomination"]
        team.name_command = request.form["name_command"]
        team.name_of_organization = request.form["name_of_organization"]
        team.competition_id = competition_id
        team.manager = request.form["manager"]
        team.number_phone_of_manager = request.form["number_phone_of_manager"]
        team.email_of_manager = request.form["email_of_manager"]
        team.name_first_member = request.form["name_first_member"]
        team.last_name_first_member = request.form["last_name_first_member"]
        team.middle_name_first_member = request.form["middle_name_first_member"]
        team.date_birthday_first_member = request.form["date_birthday_first_member"]
        team.final_top = -1
        team.final_score = 0
        team.first_score = ("0, " * 10)[:-2]
        team.second_score = ("0, " * 10)[:-2]
        team.random_queue = -1
        team.nomination = request.form["nomination"]
        if team.nomination == 1:
            team.time_of_second_race = 300
            team.time_of_first_race = 300
        else:
            team.time_of_first_race = 600
            team.time_of_second_race = 600

        db_sess.add(team)
        db_sess.commit()

        return redirect("/")

    elif request.method == "GET":
        return render_template("registration_new_team.html", form=TeamForm(), create_or_redact_team_form_html="create")


# http://127.0.0.1:5000
if __name__ == "__main__":
    db_session.global_init("dataBase/database.db")
    app.run()
