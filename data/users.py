import datetime

import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    email = sa.Column(sa.String, nullable=True, unique=True, index=True)
    # here starts personal info
    pic = sa.Column(sa.String)  # путь до картинки, которую загрузил пользователь
    age = sa.Column(sa.Integer, default=0)
    sex = sa.Column(sa.String, default='Не выбран')
    profession = sa.Column(sa.String)
    about = sa.Column(sa.String)
    work_document = sa.Column(sa.String)  # путь до файла с чертовым резюме, которое загрузит после пользователь
    work_exp = sa.Column(sa.String)  # Мы будем хранить это просто в виде строки. Будет сплит - решим после
    connect_info = sa.Column(sa.String)  # удивительно, но тоже просто строка для всех контактов
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now)

    # TODO: дописать сюда связь с Project
    # project_id = sa.Column(sa.Integer, sa.ForeignKey('project.id'))

    def __repr__(self) -> str:
        return f'<{self.id}> {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
