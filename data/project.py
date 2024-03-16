from .db_session import SqlAlchemyBase
import sqlalchemy as sa
import sqlalchemy.orm as orm
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Project(SqlAlchemyBase):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    desc = sa.Column(sa.Text)
    tasks = sa.Column(sa.String)  # какие задачи решались - просто строка, где все будет храниться

    # Просто текст, где написано какие особенности были у проекта. Это опционально, однако, если пользователь напишет,
    # то оно будет выделено жирным цветом в проекте.
    project_features = sa.Column(sa.String)

    pics = sa.Column(sa.String)  # просто пути к картинкам, что будут загружены нам
    main_pic = sa.Column(sa.String)  # путь к картинке, что будет лицом проекта

    # TODO: добавить реализацию связи с пользователем
    # user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
