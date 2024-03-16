from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Введите почту', validators=[DataRequired()])
    password = PasswordField('Введите ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
