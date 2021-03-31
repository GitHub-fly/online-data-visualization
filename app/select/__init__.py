from flask import Blueprint

# 创建蓝图对象
select = Blueprint("select", __name__)

from . import api