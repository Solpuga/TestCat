from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired


class TestsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    test_type = SelectField('Тип теста', validators=[DataRequired()],
                            choices=[(1, 'Образовательный тест'), (2, 'Психологический тест')])
    is_visible = BooleanField('Открытый или нет')
    img = FileField('Изображение')
    description = TextAreaField('Описание')
    submit = SubmitField('Сохранить')
