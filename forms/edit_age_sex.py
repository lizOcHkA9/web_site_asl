from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class EditAgeSexForm(FlaskForm):
    age = IntegerField('Возраст',
                       validators=[DataRequired(), NumberRange(min=0, max=120, message="Недопустимый возраст")])
    sex = SelectField('Пол', choices=[('Не выбран', 'Не выбран'), ('Мужской', 'Мужской'), ('Женский', 'Женский')],
                      validators=[DataRequired()])
    submit = SubmitField('Сохранить')
