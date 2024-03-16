from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Введите почту', validators=[DataRequired()])
    password = PasswordField('Ваш пароль тоже надо', validators=[DataRequired()])
    password_again = PasswordField('И его еще раз надо!', validators=[DataRequired()])
    name = StringField('Представьтес (ваше имя)', validators=[DataRequired()])
    about = TextAreaField('Расскажите о себе')
    submit = SubmitField('Зарегистрироваться')
