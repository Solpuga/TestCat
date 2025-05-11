import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Test_Ask(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'test_asks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    text = sqlalchemy.Column(sqlalchemy.String)
    img = sqlalchemy.Column(sqlalchemy.String)
    answers = sqlalchemy.Column(sqlalchemy.String)
    correct_answers = sqlalchemy.Column(sqlalchemy.String)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tests.id"))
    test = orm.relationship("Test")


class Survey_Ask(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'survey_asks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    text = sqlalchemy.Column(sqlalchemy.String)
    img = sqlalchemy.Column(sqlalchemy.String)
    answers = sqlalchemy.Column(sqlalchemy.String)
    survey_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("surveys.id"))
    survey = orm.relationship("Survey")
