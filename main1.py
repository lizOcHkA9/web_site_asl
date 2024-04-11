import os
from flask import Flask, render_template, request, make_response, session, redirect, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from data import db_session
import datetime
from flask_login import LoginManager, login_required, current_user
from register import login1, logout1, register1
from forms.edit_age_sex import EditAgeSexForm
from forms.edit_about_resume import EditAboutResumeForm
from forms.profession import ProfessionForm
from forms.experience import ExperienceForm
from forms.contact import ContactLinksForm
from data.users import User
from loguru import logger
import markdown
import json
from sqlalchemy.sql import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_123'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['UPLOAD_FOLDER'] = './uploaded/'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/add_contact_links/<int:user_id>', methods=['GET', 'POST'])
def contact_links(user_id):
    if current_user.id != user_id:
        return 'Access denied'

    form = ContactLinksForm()
    db = db_session.create_session()
    user = db.query(User).get(user_id)

    if form.validate_on_submit():
        logger.debug(f'Contact links recieved -> {form.data}')

        links = ';'.join([v for k, v in form.data.items() if 'link' in k])
        user.connect_info = links
        db.commit()
        return redirect('/portfolio')
    return render_template('contact_links.html', form=form)


@app.route('/add_experience/<int:user_id>', methods=['GET', 'POST'])
def experience(user_id):
    if current_user.id != user_id:
        return 'Access denied'

    form = ExperienceForm()
    db = db_session.create_session()
    user = db.query(User).get(user_id)

    if request.method == 'POST':

        logger.debug(f'Getting the result the experience form -> {form.experiences.data}')
        new_data = []
        for idx, el in enumerate(form.experiences.data):
            new_data.append({
                'company': el['company'],
                'position': el['position'],
                'start_date': str(el['start_date']),
                'end_date': str(el['end_date'])
            })

        work_exp = json.dumps(new_data, ensure_ascii=False)
        user.work_exp = work_exp
        db.commit()

        return redirect('/portfolio')

    return render_template('experience.html', form=form)


@app.route('/add_profession/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profession(user_id):
    if current_user.id != user_id:
        return 'Access denied'

    db = db_session.create_session()
    form = ProfessionForm()
    if form.validate_on_submit():
        user = db.query(User).get(user_id)
        selected_professions = form.professions.data
        logger.debug(f'Selected profs received -> {selected_professions}')
        user.profession = ';'.join(selected_professions)
        db.commit()
        flash('Ваши профессиональные данные сохранены.')
        return redirect('/portfolio')
    return render_template('add_profession.html', title='Редактирование профессии', form=form)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    first_5_users = db_sess.query(User).all()[:5]
    itog_first_5_users = []
    for el in first_5_users:
        el.about = markdown.markdown(el.about)
        itog_first_5_users.append(el)
    params = {
        'title': 'Portfolio',
        'users': itog_first_5_users,
        'current_user': current_user,
    }
    return render_template('index.html', **params)


@app.route('/portfolio')
@login_required
def portfolio():
    try:
        exp_arr = json.loads(current_user.work_exp)
    except Exception as e:
        exp_arr = []
        logger.warning(f'Cannot find any info about work_exp')
    params = {
        'user': current_user,
        'about': markdown.markdown(current_user.about),
        'exp_arr': exp_arr,
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


@app.route('/edit_about_resume/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_about_resume(user_id):
    if current_user.id != user_id:
        return 'Access denied'

    logger.debug('Editing about and resume...')

    db = db_session.create_session()
    user_info = db.query(User).get(user_id)

    form = EditAboutResumeForm()
    if form.validate_on_submit():  # Проверяем, валидна ли форма
        user_info.about = form.about.data
        resume_file = form.resume.data
        # Проверяем, есть ли уже сохраненный файл резюме
        if current_user.work_document:
            logger.debug('Founded file')

            # Помещаем полный путь к уже существующему файлу
            existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.work_document)
            # Проверяем, существует ли файл
            if os.path.isfile(existing_file_path):
                logger.debug('Deleting existing work_document')
                # Удаляем файл из файловой системы
                os.remove(existing_file_path)

        # Сохраняем новый файл, если он был загружен
        if resume_file:
            logger.debug('Saving new work_document...')
            # Генерируем безопасное имя файла и сохраняем его
            filename = secure_filename(resume_file.filename)
            logger.debug(f'Current work_document secure filename is - {filename}')

            unique_filename = str(current_user.id) + "_" + datetime.datetime.now().strftime(
                "%Y%m%d%H%M%S") + "_" + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            resume_file.save(file_path)
            user_info.work_document = unique_filename

        db.commit()
        return redirect('/portfolio')
    elif request.method == 'GET':  # Заполняем форму текущими данными пользователя
        form.about.data = user_info.about
    return render_template('edit_about_resume.html', form=form, upload_dir=app.config['UPLOAD_FOLDER'])


@app.route('/search', methods=['GET', 'POST'])
def parse_and_show_index():
    if request.method == 'POST':
        txt = request.form
        print(txt)
        if txt == "":
            return redirect('/index')
        db_sess = db_session.create_session()
        first_5_users = db_sess.execute(text("SELECT * FROM users WHERE name = :name"), params={"name": txt}).fetchall()[:5]
        itog_first_5_users = []
        for el in first_5_users:
            el.about = markdown.markdown(el.about)
            itog_first_5_users.append(el)
        params = {
            'title': 'Portfolio',
            'users': itog_first_5_users,
            'current_user': current_user,
        }
    if request.method == "GET":
        return render_template('index.html', **params)


@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


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
