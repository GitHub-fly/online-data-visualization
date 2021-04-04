from . import database
from flask import Flask, request
from sqlalchemy import create_engine
import pymysql

from ...utils.APIResponse import APIResponse

# 数据库连接对象
conn = None


@database.route("/conn", methods=["POST"])
def change_sql_conn():
    global conn
    conn_obj = request.get_json()  # get_json() 返回 dict 类型
    sql_type = conn_obj['sqlType'].lower()
    try:
        if sql_type == 'mysql':
            engine = create_engine('{}+pymysql://{}:{}@{}:{}/{}'.format(
                str(conn_obj['sqlType']).lower(), conn_obj['userName'], conn_obj['password'], conn_obj['host'],
                conn_obj['port'], conn_obj['database']
            ))
            conn = engine.connect()
        elif sql_type == 'postgresql':
            engine = create_engine('{}://{}:{}@{}:{}/{}'.format(
                str(conn_obj['sqlType']).lower(), conn_obj['userName'], conn_obj['password'], conn_obj['host'],
                conn_obj['port'], conn_obj['database']
            ))
            conn = engine.connect()
    except BaseException:
        return APIResponse(400, '连接失败').body()
    return APIResponse(200, '连接成功').body()
