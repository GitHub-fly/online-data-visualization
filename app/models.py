"""
    所有涉及到的实体类的文件
"""
from app.main import db


class TDataType(db.Model):
    __tablename__ = 't_datatype'
    id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(150))
    name = db.Column(db.String(150), unique=True)
    is_disabled = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    def jsondata(self):
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


class Tb_1(db.Model):
    __tablename__ = 'tb_1'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    num = db.Column(db.Integer)

    def tb_1_dict(self):
        """
        将对象转换为字典数据
        :return:
        """
        return {
            'id': self.id,
            'price': self.price,
            'num': self.num
        }
