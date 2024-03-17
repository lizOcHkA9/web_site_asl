from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from ALLOWED_PROFESSIONS import ALLOWED_PROFESSIONS


class ProfessionForm(FlaskForm):
    professions = SelectMultipleField('Профессии', choices=[(prof, prof) for prof in ALLOWED_PROFESSIONS],
                                      validators=[DataRequired()])
    submit = SubmitField('Отправить')
