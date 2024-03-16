from flask import Flask, render_template, redirect, request, make_response, session
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.loginform import LoginForm
from forms.user import RegisterForm
from loguru import logger


def login1():
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug(f'Logging in...')
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            logger.debug(f'Passwd matched')
            try:
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            except Exception as e:
                logger.error(f'Error by logging in\n{e}')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def logout1():
    logout_user()
    return redirect('/')


def register1():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='регистрация', form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='регистрация', form=form,
                                   message='такой пользователь уже есть')

        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='регистрация', form=form)
