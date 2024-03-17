from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, DateField
from wtforms.validators import DataRequired
from datetime import datetime


# Форма для одного опыта работы
class WorkExperienceForm(FlaskForm):
    company = StringField('Компания', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    start_date = DateField('Дата начала', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('Дата окончания', validators=[DataRequired()], format='%Y-%m-%d')


# Основная форма, содержащая список опыта работы
class ExperienceForm(FlaskForm):
    experiences = FieldList(FormField(WorkExperienceForm), min_entries=1)
    submit = SubmitField('Отправить')
