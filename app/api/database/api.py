from . import database
from flask import Flask, request
from sqlalchemy import create_engine

from ...utils.APIResponse import APIResponse

# 数据库连接对象
conn = None


@database.route("/conn", methods=["POST"])
def change_sql_conn():
    # get_json() 返回 dict 类型
    global conn
    conn_obj = request.get_json()

    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        conn_obj['userName'], conn_obj['password'], conn_obj['host'], conn_obj['port'], conn_obj['database']
    ))
    try:
        conn = engine.connect()
    except BaseException:
        res = APIResponse(400, '连接失败')
        return res.body()
    res = APIResponse(200, '连接成功')
    return res.body()
