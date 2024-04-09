from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    desc = TextAreaField('Описание проекта', validators=[DataRequired()])
    tasks = TextAreaField('Какие задачи вы выполняли')
    project_features = TextAreaField('Какие фичи были в вашем проекте')
    pics = MultipleFileField('Загрузите картинки работы вашего проекта!',
                     validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Только картинки!')])
    main_pic = FileField('Загрузите главную картинку вашего проекта',
                         validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Только картинки опять...'),
                                     DataRequired()])
    submit = SubmitField('Добавить проект')