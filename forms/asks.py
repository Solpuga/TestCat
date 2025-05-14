from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class TestAsksForm(FlaskForm):
    ask = StringField('Текст вопроса', validators=[DataRequired()])
    ask_type = SelectField('Тип вопроса', validators=[DataRequired()], choices=[
        (1, 'Вопрос с одиночным вариантом ответа'), (2, 'Вопрос с множественным вариантом ответа')])
    submit = SubmitField("Сохранить")

class SurveyAsksForm(FlaskForm):
    ask = StringField('Текст вопроса', validators=[DataRequired()])
