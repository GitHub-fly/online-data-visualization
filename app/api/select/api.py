from . import select  # . 表示同目录层级下
from app.utils.APIResponse import APIResponse
from sqlalchemy import create_engine
import psycopg2
from app.utils.databaseUtil import get_post_conn, close_con
from flask import request
import pandas as pd
import os


@select.route("/uploadFile", methods=["POST"])
def upload_file():
    files = request.files
    file_list = files.getlist('file')
    li = []
    for file in file_list:
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, keep_default_na=False, header=None)
            li = data.values.tolist()
        else:
            columns = pd.read_excel(file, keep_default_na=False).columns
            rows = pd.read_excel(file, keep_default_na=False).values
            li.append(columns.to_list())
            print(type(rows))
            for i in rows:
                li.append(i.tolist())
    return APIResponse(200, li).body()


@select.route("/allTable", methods=["POST"])
def select_all_table():
    """
        {
            "sqlType": "mysql",
            "userName": "root",
            "password": "root",
            "host": "localhost",
            "port": "3306",
            "database": "db_mysql"
        }
    """
    print('============================进入all_table接口============================')
    # 获取前端传来的连接对象
    conn_obj = request.get_json()
    # print("连接对象：", conn_obj)
    # 定义空数组，盛放连接中所有的表名
    table_name_all = []

    # 如果数据库类型是PG
    if conn_obj['sqlType'] == 'postgresql':
        # 使用psycopg2库连接PG数据库
        conn = psycopg2.connect(database=str(conn_obj['database']).lower(), user=conn_obj['userName'],
                                password=conn_obj['password'],
                                host=conn_obj['host'], port=conn_obj['port'])
        # 获取游标
        cursor = conn.cursor()
        # 执行sql
        cursor.execute("select * from pg_tables where schemaname = 'public'")
        # 接收返回结果集
        data = cursor.fetchall()
        # 关闭数据库连接
        conn.close()
        # 循环结果集（结果集格式为列表套元组）
        for d in data:
            # 将元组中需要的元素 => 表名，组成新的列表
            table_name_all.append(d[1])
    else:  # 如果数据库类型是MySQL
        engine_str = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(conn_obj['userName'],
                                                             conn_obj['password'], conn_obj['host'],
                                                             conn_obj['port'], conn_obj['database'])
        engine = create_engine(engine_str)
        # 构建sql查询语句
        sql_str = "SELECT table_name FROM information_schema.tables WHERE table_schema='{}'" \
            .format(conn_obj['database'])
        # 执行sql，得到查询结果
        df = pd.read_sql(sql_str, engine)
        # 将DF型的查询结果转为list型
        table_name_all = df['TABLE_NAME'].tolist()
    print("所有表名的查询结果：")
    print(table_name_all)
    return APIResponse(200, table_name_all).body()



@select.route("/allColumn", methods=["POST"])
def select_all_column():
    """
    {
        "tableName": "sample_1k_flts",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }
    """
    print('============================进入all_column接口============================')
    # 接收前端参数
    conn_obj = request.get_json()
    column_all = []

    if conn_obj['sqlType'] == 'postgresql':
        # 连接PG数据库
        postgres_engine = create_engine('{}://{}:{}@{}:{}/{}'.format(
            str(conn_obj['sqlType']).lower(), conn_obj['userName'], conn_obj['password'], conn_obj['host'],
            conn_obj['port'], conn_obj['database']
        ))
        # 执行sql
        data = pd.read_sql(
            "select * from information_schema.columns where table_schema='public' and table_name=%(name)s",
            con=postgres_engine, params={'name': conn_obj['tableName']})

        # pandas的数据输出显示设置
        pd.set_option('display.max_columns', 1000)  # 最大列数
        pd.set_option('display.max_colwidth', 20)   # 最大列宽
        pd.set_option('display.width', 1000)        # 显示区域的总宽度，以总字符数计算

        print(data)
        # 取出数据帧中 “column_name” 列所有数据 => 该数据库下所有表名 ，并把dataFrame型转为list型
        column_all = data['column_name'].tolist()
    else:
        # 连接MySQL数据库
        engine_str = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(conn_obj['userName'],
                                                             conn_obj['password'], conn_obj['host'],
                                                             conn_obj['port'], conn_obj['database'])
        mysql_engine = create_engine(engine_str)
        # 构建sql查询语句
        sql_str = "SELECT column_name FROM information_schema.`COLUMNS` WHERE table_name='{}'" \
            .format(conn_obj['tableName'])
        # 执行sql，得到查询结果
        df = pd.read_sql(sql_str, mysql_engine)
        column_all = df['COLUMN_NAME'].tolist()
    print("所有字段的查询结果：")
    print(column_all)
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
