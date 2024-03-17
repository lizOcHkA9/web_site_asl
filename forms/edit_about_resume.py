from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


# Класс формы для профиля пользователя
class EditAboutResumeForm(FlaskForm):
    about = TextAreaField('Расскажите о себе! (не стесняйтесь)', validators=[DataRequired()])
    resume = FileField(
        'Загрузите ваше резюме в виде файла!',
        validators=[FileAllowed(['pdf', 'doc', 'docx'], 'Только PDF или текстовые документы!')]
    )
    submit = SubmitField('Сохранить')
