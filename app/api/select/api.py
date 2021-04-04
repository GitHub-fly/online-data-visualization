from . import select  # . 表示同目录层级下
from app.models import Tb_1
from app.utils.APIResponse import APIResponse


@select.route("/test", methods=["GET"])
def test():
    tb = Tb_1.query.get(2).tb_1_dict()
    res = APIResponse(200, tb)
    return res.body()

