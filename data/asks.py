import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class TestAsk(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'test_asks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    text = sqlalchemy.Column(sqlalchemy.String)
    img = sqlalchemy.Column(sqlalchemy.String)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tests.id"))
    test = orm.relationship("Test")
    answers = orm.relationship("TestAnswer", back_populates='ask')


class SurveyAsk(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'survey_asks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    text = sqlalchemy.Column(sqlalchemy.String)
    img = sqlalchemy.Column(sqlalchemy.String)
    survey_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("surveys.id"))
    survey = orm.relationship("Survey")
    answers = orm.relationship("SurveyAnswer", back_populates='ask')


class TestAnswer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'test_answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    correctable = sqlalchemy.Column(sqlalchemy.String)
    ask_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("test_asks.id"))
    ask = orm.relationship("TestAsk")


class SurveyAnswer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'survey_answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    ask_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("survey_asks.id"))
    ask = orm.relationship("SurveyAsk")
