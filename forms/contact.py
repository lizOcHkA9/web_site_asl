from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, URL


class ContactLinksForm(FlaskForm):
    link_1 = StringField('Ссылка 1', validators=[Optional(), URL(message='Введите корректную ссылку')])
    link_2 = StringField('Ссылка 2', validators=[Optional(), URL(message='Введите корректную ссылку')])
    link_3 = StringField('Ссылка 3', validators=[Optional(), URL(message='Введите корректную ссылку')])
    link_4 = StringField('Ссылка 4', validators=[Optional(), URL(message='Введите корректную ссылку')])
    link_5 = StringField('Ссылка 5', validators=[Optional(), URL(message='Введите корректную ссылку')])
    submit = SubmitField('Отправить')
