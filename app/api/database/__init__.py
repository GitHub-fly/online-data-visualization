from flask import Blueprint

# 创建蓝图对象
database = Blueprint("database", __name__)

from . import api
