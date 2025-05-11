from datetime import datetime
from data.tests import Test
from data.users import User
from data.surveys import Survey
from data.asks import Test_Ask, Survey_Ask
from forms.users import LoginForm, RegisterForm, EditForm
from forms.tests import TestsForm
from forms.asks import AsksForm
from forms.surveys import SurveysForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify, make_response
from flask_restful import Api
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    tests = db_sess.query(Test)
    return render_template("index.html", tests=tests, title='TestCat')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditForm()
    # form.login.data = current_user.login
    form.surname.data = current_user.surname
    form.name.data = current_user.name
    form.email.data = current_user.email
    form.phone_number.data = current_user.phone_number
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('edit_user.html', title='Редактирование профиля',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('edit_user.html', title='Редактирование профиля',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # if db_sess.query(User).filter(User.login == form.login.data).first():
        #     return render_template('edit_user.html', title='Редактирование профиля',
        #                            form=form,
        #                            message="Логин занят")
        # current_user.login = form.login.data
        current_user.surname = form.surname.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        # current_user.phone_number = form.phone_number.data
        current_user.set_password(form.password.data)
        current_user.modified_date = datetime.now
        db_sess.commit()
        return redirect('/login')
    return render_template('edit_user.html', title='Редактирование профиля', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/tests")
def show_tests():
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.is_visible)
    return render_template("tests.html", tests=tests, title='Тесты')


@app.route("/tests/<int:tests_id>")
def show_test(tests_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.is_visible, Test.id == tests_id).first()
    if test:
        return render_template("testing.html", test=test, title=test.title)
    else:
        abort(404)


@app.route("/surveys")
def show_surveys():
    db_sess = db_session.create_session()
    surveys = db_sess.query(Survey).filter(Survey.is_visible)
    if surveys:
        return render_template("surveys.html", surveys=surveys, title='Опросы')
    else:
        abort(404)


@app.route("/surveys/<int:surveys_id>")
def show_survey(surveys_id):
    db_sess = db_session.create_session()
    survey = db_sess.query(Survey).filter(Survey.is_visible, Survey.id == surveys_id).first()
    return render_template("survey.html", surveys=survey, title=survey.title)


@app.route('/add_tests', methods=['GET', 'POST'])
@login_required
def add_tests():
    form = TestsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tests = Test()
        tests.title = form.title.data
        tests.creator_id = current_user.id
        tests.is_visible = form.is_visible.data
        tests.test_type = form.test_type.data
        current_user.tests.append(tests)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/my_tests')
    return render_template('add_tests.html', title='Добавление теста',
                           form=form)


@app.route('/edit_tests/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_tests(test_id):
    form = TestsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tests = db_sess.query(Test).filter(Test.id == test_id, Test.creator == current_user).first()
        if tests:
            form.title.data = tests.title
            form.test_type.data = tests.test_type
            form.is_visible.data = tests.is_visible
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tests = db_sess.query(Test).filter(Test.id == test_id, Test.creator == current_user).first()
        if tests:
            tests.title = form.title.data
            tests.test_type = form.test_type.data
            tests.is_visible = form.is_visible.data
            db_sess.commit()
            return redirect('/my_tests')
        else:
            abort(404)
    return render_template('edit_tests.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/tests_delete/<int:tests_id>', methods=['GET', 'POST'])
@login_required
def tests_delete(tests_id):
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.id == tests_id, Test.creator == current_user).first()
    if tests:
        db_sess.delete(tests)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_tests')


@app.route('/my_tests/<test_id>/add_ask', methods=['GET', 'POST'])
@login_required
def add_test_ask(tests_id):
    form = TestAskForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tests = Test()
        tests.title = form.title.data
        tests.creator_id = current_user.id
        tests.is_visible = form.is_visible.data
        tests.test_type = form.test_type.data
        current_user.tests.append(tests)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/my_tests')
    return render_template('tests.html', title='Добавление теста',
                           form=form)


@app.route('/my_tests/<int:tests_id>/edit_ask/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def edit_test_ask(test_id, ask_id):
    form = TestAskForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tests = db_sess.query(Test).filter(Test.id == test_id).first()
        if tests:
            form.title.data = tests.title
            form.test_type.data = tests.test_type
            form.is_visible.data = tests.is_visible
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tests = db_sess.query(Test).filter(Test.id == test_id).first()
        if tests:
            tests.title = form.title.data
            tests.test_type = form.test_type.data
            tests.is_visible = form.is_visible.data
            db_sess.commit()
            return redirect('/my_tests')
        else:
            abort(404)
    return render_template('departments.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/my_tests/<int:tests_id>/ask_delete/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def ask_delete(ask_id):
    db_sess = db_session.create_session()
    ask = db_sess.query(Test_Ask).filter(Test_Ask.id == ask_id).first()
    if ask:
        db_sess.delete(ask)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_tests')


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
