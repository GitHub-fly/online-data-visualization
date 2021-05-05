from flask import Blueprint

# 创建蓝图对象
login = Blueprint("login", __name__)

from . import api
