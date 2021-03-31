from flask import Blueprint

# 创建蓝图对象
add = Blueprint("add", __name__)

from . import api
