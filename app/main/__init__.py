"""
    初始化 app、db
    注册蓝图
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config_map
from flask_cors import *

db = SQLAlchemy()  # 没有参数的实例化数据库对象，"先上车，后补票"


def create_app(dev_name):
    """
        返回一个实例化并且配置好数据的一个 app
        dev_name： 选择环境的参数
    """
    app = Flask(__name__)

    # @app.after_request
    # def after(resp):
    #     resp = make_response(resp)
    #     resp.headers['Access-Control-Allow-Origin'] = '*'
    #     resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    #     resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with, Content-Type, Authorization'
    #     # resp.headers['Content-Type'] = 'application/json'
    #     return resp

    # 让本地服务器所有的 URL 都允许跨域请求
    CORS(app, resources=r'/*')
    config_class = config_map.get(dev_name)
    app.config.from_object(config_class)  # 从类中读取需要的信息
    app.config['JSON_AS_ASCII'] = False
    db.init_app(app)  # 实例化的数据库配置信息

    # 注册蓝图
    from app.api import add, delete, select, update, database, login
    # 绑定包里面的蓝图对象
    app.register_blueprint(add.add, url_prefix="/add")
    app.register_blueprint(delete.delete, url_prefix="/delete")
    app.register_blueprint(select.select, url_prefix="/select")
    app.register_blueprint(update.update, url_prefix="/update")
    app.register_blueprint(database.database, url_prefix="/database")
    app.register_blueprint(login.login, url_prefix="/login")
    return app
