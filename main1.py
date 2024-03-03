from flask import Flask, render_template, request, make_response, session
from data import db_session
import datetime
from flask_login import LoginManager, login_required
from register import login1, logout1, register1


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_123'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def index():
    return render_template('base.html', title='k')

@app.route('/register', methods=['GET', 'POST'])
def register():
    register1()

@app.route('/cookie_test')
def cookie_test():
    visits_count = int(request.cookies.get('visits_count', 0))
    if visits_count:
        res = make_response(f'ggggggg {visits_count + 1}')
        res.set_cookie('visits_count', str(visits_count + 1), max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(f'Вы перешли первый раз')
        res.set_cookie('visits_count', str(1), max_age=60 * 60 * 24 * 365 * 2)
    return res    

@app.route('/session_test')
def session_test():
    visits_count = session.get('visit_count', 0)
    session['visit_count'] = visits_count + 1
    return make_response(f'hvdhvjdhjxvhjb {visits_count + 1} jhvbf')

# @login_manager.user_loader
# def load_user(user_id):
#     db_sess = db_session.create_session()
#     return db_sess.query(User).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login1()


@app.route('/logout')
@login_required
def logout():
    logout1()

if __name__ == "__main__":
    db_session.global_init("db/posts.db")
    app.run(port='8080', host='127.0.0.1')
    