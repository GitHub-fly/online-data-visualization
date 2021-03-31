from flask import Blueprint

# 创建蓝图对象
delete = Blueprint("delete", __name__)

from . import api
