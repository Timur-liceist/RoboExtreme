import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

class NewRegistration(SqlAlchemyBase):
    __tablename__ = 'registrations'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    final_top = sqlalchemy.Column(sqlalchemy.Integer)
    competition_id = sqlalchemy.Column(sqlalchemy.Integer)
    team_id = sqlalchemy.Column(sqlalchemy.Integer)
    nomination_id = sqlalchemy.Column(sqlalchemy.Integer)
    final_score = sqlalchemy.Column(sqlalchemy.Integer)