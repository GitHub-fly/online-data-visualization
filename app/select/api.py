from . import select    # . 表示同目录层级下
from app.models import Tb_1


@select.route("/test", methods=["POST"])
def test():
    tb = Tb_1.query.get(2)
    print('获取数据库中id为2的price值')
    print(tb.price)
    return str(tb.price)
