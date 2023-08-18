from sqlalchemy import Column, Integer, Text
from .db_session import SqlAlchemyBase


class Competition(SqlAlchemyBase):
    __tablename__ = 'competition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Text)
    commentary = Column(Text)
    date_of_ending_registration_members = Column(Text)