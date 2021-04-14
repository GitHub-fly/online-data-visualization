from . import select  # . 表示同目录层级下
from app.utils.APIResponse import APIResponse
from sqlalchemy import create_engine
import psycopg2
from app.utils.databaseUtil import get_post_conn, close_con
from flask import request
import pandas as pd
import os


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
    air_conn = get_post_conn(conn_obj)
    # 获取游标
    air_cursor = air_conn.cursor()
    # 执行sql
    air_cursor.execute("select * from pg_tables where schemaname = 'public'")
    # 接收返回结果集
    data = air_cursor.fetchall()
    # 关闭连接
    close_con(air_conn, air_cursor)
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
    """
    查询指定数据库中某表的所有数据，采用分页实现
    limitCount：可选项，默认为100条
    其它属性为必选项
    {
        "tableName": "ncov_china",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres",
        "page": 1,
        "limitCount": 100
    }
    :return:
    """
    # 接收前端参数
    select_obj = request.get_json()
    conn = get_post_conn(select_obj)
    cur = conn.cursor()
    # 第几页
    page = select_obj['page'] - 1
    limit_count = 100
    # 判断前端传递过来的参数中是否含有 'limitCount'
    if hasattr(select_obj, 'limitCount'):
        # 每页多少条数据
        limit_count = select_obj['limitCount']
    # 开始查询的起点
    start = page * limit_count
    cur.execute('SELECT * FROM {} LIMIT {} offset {};'.format(select_obj['tableName'], limit_count, start))
    data = cur.fetchall()
    print(data)
    close_con(conn, cur)
    return APIResponse(200, data).body()


@select.route("/addDataByColumn", methods=["POST"])
def select_all_table_column():
    obj = request.get_json()
    conn = get_post_conn(obj)
    cur = conn.cursor()
    # 第几页
    page = obj['page'] - 1
    limit_count = 100
    # 判断前端传递过来的参数中是否含有 'limitCount'
    if hasattr(obj, 'limitCount'):
        # 每页多少条数据
        limit_count = obj['limitCount']
    # 开始查询的起点
    start = page * limit_count
    cur.execute('SELECT {} FROM {} LIMIT {} offset {};'.format(obj['columnName'], obj['tableName'], limit_count, start))
    data = cur.fetchall()
    print(data)
    close_con(conn, cur)
    return APIResponse(200, data).body()
