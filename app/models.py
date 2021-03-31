"""
    所有涉及到的实体类的文件
"""
from app.main import db


class Tb_1(db.Model):
    __tablename__ = 'tb_1'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    num = db.Column(db.Integer)
