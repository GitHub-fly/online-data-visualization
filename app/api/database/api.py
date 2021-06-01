from . import database
from flask import request
from sqlalchemy import create_engine

from manage import db
from ...utils.APIResponse import APIResponse
import app.models as md
from flask import current_app as app

from ...utils.databaseUtil import get_post_conn


@database.route("/conn", methods=["POST"])
def change_sql_conn():
    conn = {}
    conn_obj = request.get_json()  # get_json() 返回 dict 类型
    print(conn_obj)
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
    except Exception:
        print('连接失败！')
        return APIResponse(400, '连接失败').body()
    print('连接成功！')
    print('关闭数据库连接')
    conn.close()
    return APIResponse(200, '连接成功').body()


@database.route("/allDataTypeInfo", methods=["POST"])
def get_data_type_info():
    """
    查询所有的可接入数据源的数据
    :return:
    """
    li = md.TDataType.query.filter_by(is_disabled=1).all()
    res_li = []
    for item in li:
        res_li.append(item.json_data())
    app.logger.info("查询所有的可接入数据源的数据:" + str(res_li)[0:30] + '.....')
    return APIResponse(200, res_li).body()


@database.route("/uploadSql", methods=["POST"])
def upload_sql():
    obj = request.get_json()
    conn = get_post_conn(obj)
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from {obj['tableName']}")
    data = cursor.fetchall()
    conn.close()
    cursor.close()
    app.logger.info('记录该用户调用上传 sql 文件接口信息')
    user_api_bhv = md.UserApiBhv(user_id=obj['userId'], data_count=data, api_name="上传 sql 文件接口")
    db.session.add(user_api_bhv)
    record = md.TRecord(user_id=obj['userId'], name='', upload_type=2)
    db.session.add(record)
    return APIResponse(200, '上传成功').body()
