import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    test_type = sqlalchemy.Column(sqlalchemy.String)
    img = sqlalchemy.Column(sqlalchemy.String, default='img/fon_cat.png')
    description = sqlalchemy.Column(sqlalchemy.String)
    is_visible = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    creator = orm.relationship("User")
    asks = orm.relationship("TestAsk", back_populates='test')



