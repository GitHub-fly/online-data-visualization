from flask import Blueprint

# 创建蓝图对象
update = Blueprint("update", __name__)

from . import api