from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired


class TestAsksForm(FlaskForm):
    ask = StringField('Текст вопроса', validators=[DataRequired()])
    # ask_type = SelectField('Тип вопроса', validators=[DataRequired()], choices=[
    #     (1, 'Вопрос с одиночным вариантом ответа'), (2, 'Вопрос с множественным вариантом ответа')])
    img = FileField('Изображение')
    save = SubmitField("Сохранить")

class SurveyAsksForm(FlaskForm):
    ask = StringField('Текст вопроса', validators=[DataRequired()])
    img = FileField('Изображение')
    save = SubmitField("Сохранить")

class AnswerForm(FlaskForm):
    text = StringField('Вариант ответа', validators=[DataRequired()])
    is_correct = BooleanField('Верный или нет')
    submit = SubmitField("Cохранить")