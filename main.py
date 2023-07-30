import hashlib

from flask import Flask, render_template, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import redirect

from for_work_with_database import db_session
from for_work_with_database.class_db_competition import Competition
from for_work_with_database.class_db_reg_team import TeamDB
from for_work_with_database.class_db_registration import NewRegistration
from for_work_with_database.class_db_user import User

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from forms.LoginForm import LoginForm
from forms.NewCompetition import NewCompetition
from forms.RegTeamForm import TeamForm

app = Flask(__name__)
app.secret_key = "roboExtreme"
limiter = Limiter(get_remote_address, app=app)

login_manager = LoginManager()

login_manager.init_app(app)


@app.route("/create_new_competition", methods=["POST", "GET"])
def create_new_competition():
    if request.method == "POST":
        if not request.form["date_of_start_competition"]:
            return render_template('new_competition.html',
                                   message="Вы не выбрали дату начала соревнования",
                                   form=NewCompetition())
        if not request.form["commentary_for_competition"]:
            return render_template('new_competition.html',
                                   message="Вы не написали комментарии к соревнованию",
                                   form=NewCompetition())
        print("added")
        db_sess = db_session.create_session()
        new_competition = Competition()
        print("date_of_start =", request.form["date_of_start_competition"])
        new_competition.date = request.form["date_of_start_competition"]
        new_competition.commentary = request.form["commentary_for_competition"]
        db_sess.add(new_competition)
        db_sess.commit()
        return redirect("/")
    elif request.method == "GET":
        return render_template("new_competition.html", form=NewCompetition())


# @app.route("/reg_team")
# def reg_team
@app.route("/")
@limiter.limit("5/second")
def main_page():
    # print(current_user.role_id)
    if current_user.is_authenticated:
        print(current_user.email)
    sess = db_session.create_session()
    competitions = sess.query(Competition).all()
    print(competitions)

    # return render_template("main_page.html", competitions=competitions)
    return render_template("main_page.html", competitions=competitions)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@limiter.limit("5/second")
@login_required
def logout():
    logout_user()
    return redirect("/")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/login_user", methods=["GET", "POST"])
def login():
    print("LOGIN", )
    if request.method == "POST":
        print("POST")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form["email"]).first()
        if user and user.check_password(hash_password(request.form["password"])):
            login_user(user)
            print("LOGIN_USER")
            return redirect("/")
        return render_template('login_user.html',
                               message="Неправильный логин или пароль",
                               form=LoginForm())
    elif request.method == "GET":
        print("GET")
        return render_template("login_user.html", form=LoginForm())


@app.route("/reg_team/<int:id>", methods=["GET", "POST"])
def reg_team(id):
    print()
    if request.method == "POST":
        print("POST")
        print(request.form)
        team = TeamDB()
        print(1)
        name_command = request.form["name_command"]
        name_of_organization = request.form["name_of_organization"]
        manager = request.form["manager"]
        email_of_manager = request.form["email_of_manager"]
        number_phone_of_manager = request.form["number_phone_of_manager"]
        name_first_member = request.form["name_first_member"]
        last_name_first_member = request.form["last_name_first_member"]
        middle_name_first_member = request.form["middle_name_first_member"]
        date_birthday_second_member = request.form["date_birthday_second_member"]
        date_birthday_first_member = request.form["date_birthday_first_member"]
        certificate_PFDO_first_member = request.form["certificate_PFDO_first_member"]
        name_second_member = request.form["name_second_member"]
        last_name_second_member = request.form["last_name_second_member"]
        middle_name_second_member = request.form["middle_name_second_member"]
        certificate_PFDO_second_member = request.form["certificate_PFDO_second_member"]
        nomination = request.form["nomination"]
        team.certificate_PFDO_first_member = certificate_PFDO_first_member
        team.certificate_PFDO_second_member = certificate_PFDO_second_member
        team.last_name_second_member = last_name_second_member
        team.name_second_member = name_second_member
        team.middle_name_second_member = middle_name_second_member
        team.nomination = nomination
        team.date_birthday_second_member = date_birthday_second_member
        team.name_command = name_command
        team.name_of_organization = name_of_organization
        team.competition_id = id
        team.manager = manager
        team.number_phone_of_manager = number_phone_of_manager
        team.email_of_manager = email_of_manager
        team.name_first_member = name_first_member
        team.last_name_first_member = last_name_first_member
        team.middle_name_first_member = middle_name_first_member
        team.date_birthday_first_member = date_birthday_first_member
        db_sess = db_session.create_session()
        db_sess.add(team)
        new_registration = NewRegistration()
        new_registration.competition_id = id
        new_registration.team_id = team.id
        new_registration.nomination_id = nomination
        db_sess.add(new_registration)
        db_sess.commit()
        return redirect("/")
    elif request.method == "GET":
        return render_template("registration_new_team.html", form=TeamForm())


print(hash_password("TimkaOch2007!"))
if __name__ == "__main__":
    db_session.global_init("dataBase/database.db")
    app.run()
