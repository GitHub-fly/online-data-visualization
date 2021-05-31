"""
    所有涉及到的实体类的文件
"""
import datetime

from app.main import db


class TDataType(db.Model):
    """
    数据源对象
    """
    __tablename__ = 't_datatype'
    id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(150))
    name = db.Column(db.String(150), unique=True)
    is_disabled = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    def json_data(self):
        """
        将对象转换为字典数据
        :return:s
        """
        return {
            'id': self.id,
            'cover': self.cover,
            'name': self.name,
            'is_disabled': self.is_disabled,
            'create_time': self.create_time,
            'update_time': self.update_time
        }

    def __repr__(self):
        return '<tDataType %r>' % self.name


class UserApiBhv(db.Model):
    __tablename__ = 'user_api_bhv'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer)
    data_count = db.Column(db.Integer)
    api_name = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def json_data(self):
        """
        将对象转换为字典数据
        :return:
        """
        return {
            'id': self.id,
            'userId': self.user_id,
            'dataCount': self.data_count,
            'apiName': self.api_name,
            'create_time': self.create_time,
            'update_time': self.update_time
        }

    def __repr__(self):
        return '<userApiBhv %r>' % self.api_name
