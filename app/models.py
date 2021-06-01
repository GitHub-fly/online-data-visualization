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


class TUser(db.Model):
    """
    用户表
    """
    __tablename__ = 't_user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    account = db.Column(db.String(255))
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    is_login = db.Column(db.Integer)
    role_id = db.Column(db.Integer)
    is_disabled = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    hometown = db.Column(db.String(255))
    sex = db.Column(db.String(255))
    open_id = db.Column(db.Integer)

    def json_data(self):
        """
        将对象转换为字典数据
        :return:
        """
        return {
            'user_id': self.user_id,
            'account': self.account,
            'password': self.password,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'role_id': self.role_id,
            'is_login': self.is_login,
            'is_disabled': self.is_disabled,
            'create_time': self.create_time,
            'hometown': self.hometown,
            'update_time': self.update_time,
            'sex': self.sex,
            'open_id': self.open_id,
        }

    def __repr__(self):
        return '<TUser %r>' % self.account


class TRecord(db.Model):
    __tablename__ = 't_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer)
    parent_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    upload_type = db.Column(db.Integer)
    is_disabled = db.Column(db.Integer, default=1)
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
            'parentId': self.parent_id,
            'name': self.name,
            'uploadType': self.upload_type,
            'isDisabled': self.is_disabled,
            'createTime': self.create_time,
            'updateTime': self.update_time,
        }

    def __repr__(self):
        return '<tRecord %r>' % self.name
