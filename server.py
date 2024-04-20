import math
import os
from flask import Flask, render_template, request, make_response, session, redirect, send_from_directory, flash, jsonify, current_app
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
from data.project import Project
from forms.project_form import ProjectForm
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
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Установим количество элементов на странице
    db_sess = db_session.create_session()
    first_5_users = db_sess.query(User).all()[(page - 1) * per_page:per_page * page]
    itog_first_5_users = []
    for el in first_5_users:
        el.about = markdown.markdown(el.about)
        itog_first_5_users.append(el)
    params = {
        'title': 'Portfolio',
        'users': itog_first_5_users,
        'current_user': current_user,
        'page': page,
        'total_pages': math.ceil(len(db_sess.query(User).all()) / 5)
    }
    db_sess.close()
    return render_template('index.html', **params)


@app.route('/portfolio')
@login_required
def portfolio():
    try:
        exp_arr = json.loads(current_user.work_exp)
    except Exception as e:
        exp_arr = []
        logger.warning(f'Cannot find any info about work_exp')
    
    db = db_session.create_session()
    project_cnt = len(db.query(Project).filter_by(author=current_user.id).all())
    logger.debug(f'Project cnt -> {project_cnt}')
    params = {
        'user': current_user,
        'about': markdown.markdown(current_user.about),
        'exp_arr': exp_arr,
        'project_count': project_cnt
    }
    return render_template('portfolio.html', **params)

@app.route('/users/<int:userid>')
def get_user(userid: int):
    db = db_session.create_session()
    user_data = db.query(User).get(userid)
    try:
        exp_arr = json.loads(user_data.work_exp)
    except Exception as e:
        exp_arr = []
        logger.warning(f'Cannot find any info about work_exp')
    
    project_cnt = len(db.query(Project).filter_by(author=userid).all())
    logger.debug(f'Project cnt -> {project_cnt}')
    params = {
        'user': user_data,
        'about': markdown.markdown(user_data.about),
        'exp_arr': exp_arr,
        'project_count': project_cnt
    }
    return render_template('users_look.html', **params)

@app.route('/projects/user/<int:userid>')
def get_users_projects(userid: int):
    db = db_session.create_session()
    user_data = db.query(User).get(userid)
    projs = db.query(Project).filter_by(author=userid).all()
    logger.debug(f'All the projs of the user -> {projs}')
    
    data = []
    if projs:
        for el in projs:
            if el == '':
                continue
            proj = db.query(Project).get(int(el.id))
            data.append(proj)
    
    # pictures = [for el in data]
    
    params = {
        'projects': data,
        'user': user_data,
        'upload_dir': app.config['UPLOAD_FOLDER']
    }
    logger.debug(f'Path to uploaded files -> {params["upload_dir"]}')
    return render_template('users_look_project.html', **params)

@app.route('/my_projects')
@login_required
def my_projects():
    db = db_session.create_session()
    projs = db.query(Project).filter_by(author=current_user.id).all()
    logger.debug(f'All the projs of the user -> {projs}')
    
    data = []
    if projs:
        for el in projs:
            if el == '':
                continue
            proj = db.query(Project).get(int(el.id))
            data.append(proj)
    
    # pictures = [for el in data]
    
    params = {
        'projects': data,
        'user': current_user,
        'upload_dir': app.config['UPLOAD_FOLDER']
    }
    logger.debug(f'Path to uploaded files -> {params["upload_dir"]}')
    return render_template('my_projects.html', **params)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/add_proj/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_project(user_id: int):
    if current_user.id != user_id:
        return 'Access denied'
    
    form = ProjectForm()
    if form.validate_on_submit():
        
        def save_pictures(form_pics_field, form_main_pic_field):
            file_path_list = []
            
            # Обрабатываем поле 'pics' с множественным выбором файлов
            if form_pics_field.data:
                for file in form_pics_field.data:
                    # Генерируем уникальное имя для файла
                    unique_filename = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + '_' + secure_filename(file.filename)
                    # Сохраняем файл в папке для загрузки
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    # Добавляем имя файла в список
                    file_path_list.append(unique_filename)

            # Обрабатываем поле 'main_pic' для одного файла
            if form_main_pic_field.data:
                unique_filename = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + '_' + secure_filename(form_main_pic_field.data.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                form_main_pic_field.data.save(file_path)
                file_path_list.append(unique_filename)

            return file_path_list
        
        # gather all the pics -> last pic is always main!
        pic_list = save_pictures(form.pics, form.main_pic)
        logger.debug(f'Here the pic_list -> {pic_list}')
        
        new_project = Project(
            name=form.name.data,
            desc=form.desc.data,
            tasks=form.tasks.data,
            project_features=form.project_features.data if form.project_features.data else None,
            pics=';'.join(pic_list[:-1]),
            main_pic=pic_list[-1],
            author=user_id
        )
        # круто делаем все в БД
        db = db_session.create_session()
        db.add(new_project)
        db.commit()
        logger.debug(f'Here is the new_proj id -> {new_project.id}')
        db.close()
        
        return redirect('/my_projects')
    return render_template('create_project.html', form=form)


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
    if request.method == "POST":
        txt = request.form['search']
        if txt == "":
            return redirect('/index')
        db_sess = db_session.create_session()
        first_5_users = db_sess.query(User).filter_by(name=txt).all()[:5]
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
    else:
        return redirect("/")


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
    app.run(port=8000, host='127.0.0.1')
