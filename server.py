import math
from datetime import datetime
from data.tests import Test
from data.users import User
from data.surveys import Survey
from data.asks import TestAsk, SurveyAsk, TestAnswer, SurveyAnswer
from forms.users import LoginForm, RegisterForm, EditForm
from forms.tests import TestsForm
from forms.asks import TestAsksForm, SurveyAsksForm, AnswerForm
from forms.surveys import SurveysForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify, make_response
from flask_restful import Api
from data import db_session
from sqlalchemy.sql.expression import func
import os

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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/profile/settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    form = EditForm()
    # form.login.data = current_user.login
    form.surname.data = current_user.surname
    form.name.data = current_user.name
    form.email.data = current_user.email
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() and current_user.email != form.email.data:
            return render_template('settings.html', title='Редактирование профиля',
                                   form=form,
                                   message="Такой пользователь уже есть")
        current_user.surname = form.surname.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.modified_date = datetime.now
        db_sess.commit()
    return render_template("settings.html", form=form, title='Редактирование профиля')


@app.route("/profile/statistic")
@login_required
def account_statistic():
    return render_template("statistic.html", title='Аккаунт')


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
    tests = db_sess.query(Test).filter(Test.is_visible).all()
    return render_template("tests.html", tests=tests, title='Тесты', y=math.ceil(len(tests) / 4))


@app.route("/pashalka/228")
def pashalka():
    return render_template("pashalka.html")


@app.route("/tests/<int:tests_id>")
def testing(tests_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.is_visible, Test.id == tests_id).first()
    if test:
        return render_template("testing.html", test=test, title=test.title)
    else:
        abort(404)


@app.route("/surveys")
def show_surveys():
    db_sess = db_session.create_session()
    surveys = db_sess.query(Survey).filter(Survey.is_visible).all()
    return render_template("surveys.html", surveys=surveys, title='Опросы', y=math.ceil(len(surveys) / 4))


@app.route("/surveys/<int:surveys_id>")
def surveying(surveys_id):
    db_sess = db_session.create_session()
    survey = db_sess.query(Survey).filter(Survey.is_visible, Survey.id == surveys_id).first()
    return render_template("survey.html", surveys=survey, title=survey.title)


@app.route("/my_tests", methods=['GET', 'POST'])
@login_required
def my_tests():
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.creator_id == current_user.id).all()
    form = TestsForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        test = Test()
        test.creator_id = current_user.id
        test.title = form.title.data
        current_user.tests.append(test)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/edit_test/{db_sess.query(Test).filter(Test.creator_id == current_user.id,
                                                                 Test.id == db_sess.query(func.max(Test.id)).filter(
                                                                     Test.creator_id == current_user.id)).first().id}')
    return render_template("my_tests.html", tests=tests, title='Мои тесты', y=math.ceil(len(tests) / 4), form=form)


@app.route('/edit_test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_tests(test_id):
    form = TestsForm()

    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.creator_id == current_user.id, Test.id == test_id).first()
    if request.method == "GET":
        if tests:
            form.title.data = tests.title
            form.test_type.data = tests.test_type
            form.is_visible.data = tests.is_visible
            form.description.data = tests.description
        else:
            abort(404)
    if form.validate_on_submit():
        if tests:
            tests.title = form.title.data
            tests.test_type = form.test_type.data
            tests.description = form.description.data
            if form.img.data:
                form.img.data.save('static/test_img/' + f'{tests.id}.png')
                tests.img = 'test_img/' + f'{tests.id}.png'
            if tests.asks and form.description.data:
                tests.is_visible = form.is_visible.data
            db_sess.commit()
            return redirect('/my_tests')
        else:
            abort(404)
    return render_template('edit_tests.html',
                           title='Редактирование тесты',
                           form=form, test=tests)


@app.route('/tests_delete/<int:tests_id>', methods=['GET', 'POST'])
@login_required
def tests_delete(tests_id):
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).filter(Test.id == tests_id, Test.creator_id == current_user.id).first()
    if tests:
        if tests.img == f'test_img/{tests_id}.png':
            os.remove(f'static/test_img/{tests_id}.png')
        db_sess.delete(tests)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_tests')


@app.route('/edit_test/<int:test_id>/add_test_ask', methods=['GET', 'POST'])
@login_required
def add_test_ask(test_id):
    form = TestAsksForm()
    ask = TestAsk()
    ansform = AnswerForm()
    if form.validate_on_submit() and form.data.get('save'):
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id).first()
        ask.text = form.ask.data
        if form.img.data:
            form.img.data.save(f'static/test_ask_img/{ask.id}.png')
            ask.img = f'test_ask_img/{ask.id}.png'
        test.asks.append(ask)
        db_sess.merge(test)
        db_sess.commit()
        return redirect(f'/edit_test/{test_id}')
    if ansform.validate_on_submit() and ansform.data.get('submit'):
        answer = TestAnswer()
        answer.text = ansform.text.data
        answer.is_correct = ansform.is_correct.data
        ask.answers.append(answer)
    return render_template('add_test_ask.html', title='Добавление тестового вопроса',
                           form=form, ansform=ansform, ask=ask)


@app.route('/edit_test/<int:test_id>/edit_test_ask/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def edit_test_ask(test_id, ask_id):
    form = TestAsksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ask = db_sess.query(TestAsk).filter(Test.id == ask_id).first()
        if ask:
            form.title.data = ask.text
            form.test_type.data = tests.test_type
            form.is_visible.data = tests.is_visible
        else:
            abort(404)
    form = TestAsksForm()
    ansform = AnswerForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id).first()
        ask.text = form.ask.data
        test.asks.append(ask)
        db_sess.merge(test)
        db_sess.commit()
        return redirect(f'/edit_test/{test_id}')
    if ansform.validate_on_submit():
        answer = TestAnswer()
        answer.text = ansform.text.data
        answer.is_correct = form.is_correct.data
        ask.answers.append(answer)
    return render_template('departments.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/edit_test/<int:test_id>/test_ask_delete/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def test_ask_delete(ask_id):
    db_sess = db_session.create_session()
    ask = db_sess.query(TestAsk).filter(TestAsk.id == ask_id).first()
    if ask:
        db_sess.delete(ask)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_tests')


@app.route("/my_surveys")
@login_required
def my_surveys():
    db_sess = db_session.create_session()
    surveys = db_sess.query(Survey).filter(Survey.is_visible, Survey.creator == current_user).all()
    return render_template("my_surveys.html", surveys=surveys, title='Мои опросы', y=math.ceil(len(surveys) / 4))


#
# @app.route('/edit_survey/<int:survey_id>', methods=['GET', 'POST'])
# @login_required
# def edit_surveys(survey_id):
#     form = SurveysForm()
#     db_sess = db_session.create_session()
#     surveys = db_sess.query(Survey).filter(Survey.id == survey_id, Survey.creator == current_user).first()
#     if request.method == "GET":
#         if surveys:
#             form.title.data = surveys.title
#             form.survey_type.data = surveys.survey_type
#             form.is_visible.data = surveys.is_visible
#         else:
#             abort(404)
#     if form.validate_on_submit():
#         if surveys:
#             surveys.title = form.title.data
#             surveys.survey_type = form.survey_type.data
#             if surveys.asks:
#                 surveys.is_visible = form.is_visible.data
#             db_sess.commit()
#             return redirect('/my_surveys')
#         else:
#             abort(404)
#     return render_template('edit_surveys.html',
#                            title='Редактирование тесты',
#                            form=form, survey=surveys
#                            )
#
#
# @app.route('/surveys_delete/<int:surveys_id>', methods=['GET', 'POST'])
# @login_required
# def surveys_delete(surveys_id):
#     db_sess = db_session.create_session()
#     surveys = db_sess.query(Survey).filter(Survey.id == surveys_id, Survey.creator == current_user).first()
#     if surveys:
#         db_sess.delete(surveys)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/my_surveys')
#
#
# @app.route('/add_ask/<int:survey_id>', methods=['GET', 'POST'])
# @login_required
# def add_survey_ask(survey_id):
#     form = SurveyAsksForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         survey = db_sess.query(Survey).filter(Survey.id == survey_id).first()
#         ask = Survey_Ask()
#         ask.text = form.ask.data
#         survey.asks.append(ask)
#         db_sess.merge(survey)
#         db_sess.commit()
#         return redirect('/add_survey')
#     return render_template('add_survey_ask.html', title='Добавление теста',
#                            form=form)
#
#
# @app.route('/edit_survey_ask/<int:ask_id>', methods=['GET', 'POST'])
# @login_required
# def edit_survey_ask(ask_id):
#     form = SurveyAsksForm()
#     if request.method == "GET":
#         db_sess = db_session.create_session()
#         surveys = db_sess.query(Survey_Ask).filter(Survey_Ask.id == ask_id,
#                                                    Survey_Ask.survey.creator == current_user).first()
#         if surveys:
#             form.title.data = surveys.title
#             form.survey_type.data = surveys.survey_type
#             form.is_visible.data = surveys.is_visible
#         else:
#             abort(404)
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         surveys = db_sess.query(Survey).filter(Survey.id == ask_id).first()
#         if surveys:
#             surveys.title = form.title.data
#             surveys.survey_type = form.survey_type.data
#             surveys.is_visible = form.is_visible.data
#             db_sess.commit()
#             return redirect('/my_surveys')
#         else:
#             abort(404)
#     return render_template('departments.html',
#                            title='Редактирование департамента',
#                            form=form
#                            )


@app.route('/survey_ask_delete/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def survey_ask_delete(ask_id):
    db_sess = db_session.create_session()
    ask = db_sess.query(Survey_Ask).filter(Survey_Ask.id == ask_id, Survey_Ask.survey.creator == current_user).first()
    if ask:
        db_sess.delete(ask)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_surveys')


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
