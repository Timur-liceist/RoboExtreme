from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String

from .db_session import SqlAlchemyBase

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    last_name = Column(String)
    role_id = Column(Integer, ForeignKey('roles.id'))

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return self.password == password
