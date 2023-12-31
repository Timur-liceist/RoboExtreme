import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from .db_session import SqlAlchemyBase


class TeamDB(SqlAlchemyBase):
    __tablename__ = 'teams'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_command = sqlalchemy.Column(sqlalchemy.String)
    name_of_organization = sqlalchemy.Column(sqlalchemy.String)
    first_score = sqlalchemy.Column(sqlalchemy.Text)
    second_score = sqlalchemy.Column(sqlalchemy.Text)
    nomination = sqlalchemy.Column(sqlalchemy.Integer)
    competition_id = sqlalchemy.Column(sqlalchemy.Integer)
    manager = sqlalchemy.Column(sqlalchemy.String)
    number_phone_of_manager = sqlalchemy.Column(sqlalchemy.String)
    email_of_manager = sqlalchemy.Column(sqlalchemy.String)
    name_first_member = sqlalchemy.Column(sqlalchemy.String)
    last_name_first_member = sqlalchemy.Column(sqlalchemy.String)
    middle_name_first_member = sqlalchemy.Column(sqlalchemy.String)
    date_birthday_first_member = sqlalchemy.Column(sqlalchemy.String)
    certificate_PFDO_first_member = sqlalchemy.Column(sqlalchemy.String)
    name_second_member = sqlalchemy.Column(sqlalchemy.String)
    middle_name_second_member = sqlalchemy.Column(sqlalchemy.String)
    last_name_second_member = sqlalchemy.Column(sqlalchemy.String)
    date_birthday_second_member = sqlalchemy.Column(sqlalchemy.String)
    certificate_PFDO_second_member = sqlalchemy.Column(sqlalchemy.String)
    final_top = sqlalchemy.Column(sqlalchemy.Integer)
    final_score = sqlalchemy.Column(sqlalchemy.Integer)
    random_queue = sqlalchemy.Column(sqlalchemy.Integer)
    time_of_first_race = sqlalchemy.Column(sqlalchemy.Integer)
    time_of_second_race = sqlalchemy.Column(sqlalchemy.Integer)
    list_logs_score_of_first_race = sqlalchemy.Column(sqlalchemy.Text)
    list_logs_score_of_second_race = sqlalchemy.Column(sqlalchemy.Text)