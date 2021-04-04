"""
    所有涉及到的实体类的文件
"""
from app.main import db


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
