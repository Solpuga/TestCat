from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired


class AsksForm(FlaskForm):
    ask_type = SelectField('Тип вопроса', validators=[DataRequired()], choices=[
        (1, 'Вопрос с одиночным вариантом ответа'), (2, 'Вопрос с множественным вариантом ответа')])
    ask = StringField('Текст вопроса', validators=[DataRequired()])
    choices = SelectField('')
