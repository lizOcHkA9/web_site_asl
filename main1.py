from flask import Flask, render_template, request, make_response, session, redirect
from data import db_session
import datetime
from flask_login import LoginManager, login_required, current_user
from register import login1, logout1, register1
from forms.edit_age_sex import EditAgeSexForm
from data.users import User
from loguru import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_123'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    first_5_users = db_sess.query(User).all()[:5]
    params = {
        'title': 'Portfolio',
        'users': first_5_users,
        'current_user': current_user,
    }
    return render_template('index.html', **params)


@app.route('/portfolio')
@login_required
def portfolio():
    params = {
        'user': current_user,
    }
    return render_template('portfolio.html', **params)


@app.route('/edit_age_sex/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_age_sex(user_id):
    logger.debug('On page of editing age and sex')
    if current_user.id != user_id:
        return 'Access denied'

    db = db_session.create_session()
    user_info = db.query(User).get(user_id)
    if user_info is None:
        return "Пользователь не найден", 404

    form = EditAgeSexForm(obj=user_info)  # Сюда передадим объект для предзаполнения формы

    if form.validate_on_submit():
        logger.debug('Editing the age and sex')
        # Получаем данные из формы и обновляем информацию о пользователе
        user_info.age = form.age.data
        user_info.sex = form.sex.data
        db.commit()  # Сохраняем изменения в базу данных
        return redirect('/portfolio')

    return render_template('edit_age_sex.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    return register1()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return login1()


@app.route('/logout')
@login_required
def logout():
    return logout1()


if __name__ == "__main__":
    db_session.global_init("db/posts.db")
    app.run(port=5000, host='127.0.0.1')
