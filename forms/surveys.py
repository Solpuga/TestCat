from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SurveysForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    test_type = SelectField('Тип теста', validators=[DataRequired()], choices=[(1, 'Образовательный тест'), (2, 'Психологический тест')])
    is_visible = BooleanField('Открытый или нет', default=False)
    submit = SubmitField("Сохранить")