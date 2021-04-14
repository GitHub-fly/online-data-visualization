from sqlalchemy.orm import sessionmaker

from . import select  # . 表示同目录层级下
from app.models import Tb_1
from app.utils.APIResponse import APIResponse
from sqlalchemy import create_engine
import psycopg2
from flask import request
import pandas as pd
import os


@select.route("/test", methods=["GET"])
def test():
    tb = Tb_1.query.get(2).tb_1_dict()
    res = APIResponse(200, tb)
    return res.body()


@select.route("/uploadFile", methods=["POST"])
def upload_files():
    files = request.files
    file_list = files.getlist('file')
    print(file_list)
    li = []
    for file in file_list:
        upload_file = {}
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, keep_default_na=False, header=None)
            upload_file['name'] = file.filename
            upload_file['file_list'] = data.values.tolist()
        else:
            columns = pd.read_excel(file, keep_default_na=False).columns
            rows = pd.read_excel(file, keep_default_na=False).values
            upload_file['name'] = file.filename
            upload_file['file_list'] = []
            upload_file['file_list'].append(columns.to_list())
            for i in rows:
                upload_file['file_list'].append(i.tolist())
        li.append(upload_file)
    print(len(li))
    return APIResponse(200, li).body()


@select.route("/allTable", methods=["POST"])
def select_all_table():
    print('进入all_table')
    # 获取前端传来的连接对象
    conn_obj = request.get_json()
    print(conn_obj)
    # 使用psycopg2库连接PG数据库,database参数可为postgres
    air_conn = psycopg2.connect(database=str(conn_obj['database']).lower(), user=conn_obj['userName'],
                                password=conn_obj['password'],
                                host=conn_obj['host'], port=conn_obj['port'])
    # 获取游标
    air_cursor = air_conn.cursor()
    # 执行sql
    air_cursor.execute("select * from pg_tables where schemaname = 'public'")
    # 接收返回结果集
    data = air_cursor.fetchall()
    # 关闭数据库连接
    air_conn.close

    # 定义空数组，盛放连接中所有的表名
    tablename_all = []
    # 循环结果集（结果集格式为列表套元组）
    for d in data:
        # 将元组中需要的元素 => 表名，组成新的列表
        tablename_all.append(d[1])
    #     返回所有表名
    return APIResponse(200, tablename_all).body()


@select.route("/allColumn", methods=["POST"])
def select_all_column():
    # 接收前端参数
    select_obj = request.get_json()
    # 连接数据库
    airport_engine = create_engine('{}://{}:{}@{}:{}/{}'.format(
        str(select_obj['sqlType']).lower(), select_obj['userName'], select_obj['password'], select_obj['host'],
        select_obj['port'], select_obj['database']
    ))
    # 执行sql
    data = pd.read_sql(
        "select * from information_schema.columns where table_schema='public' and table_name=%(name)s",
        con=airport_engine, params={'name': select_obj['tableName']})
    data_h = data.head()
    # 取出数据帧中 “column_name” 列所有数据 => 该数据库下所有表名 ，并把dataFrame型转为list型
    column_all = data_h['column_name'].tolist()
    return APIResponse(200, column_all).body()


@select.route("/allData", methods=["POST"])
def select_all_data():
    # 接收前端参数
    select_obj = request.get_json()
    # 连接数据库
    airport_engine = create_engine('{}://{}:{}@{}:{}/{}'.format(
        str(select_obj['sqlType']).lower(), select_obj['userName'], select_obj['password'], select_obj['host'],
        select_obj['port'], select_obj['database']
    ))

    # Session = sessionmaker(bind = airport_engine)
    # session = Session()
    #
    # data = session.query((select_obj['tableName']))

    data = pd.read_sql("select * from name")

    print(data.tolist())

    return APIResponse(200, data.tolist()).body()
