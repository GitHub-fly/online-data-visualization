import time
import pandas as pd
import os
import json
import simplejson as spjson

from decimal import *
from datetime import datetime
from . import select  # . 表示同目录层级下
from app.utils.APIResponse import APIResponse
from sqlalchemy import create_engine
from app.utils.databaseUtil import get_post_conn, close_con, paging, get_post_engine
from flask import request
from .service.selectService import get_file_chart_data, get_sql_chart_data
from ...common.EnumList import FunType
from ...common.Global import all_data_list
from ...models import UserApiBhv
from ...utils.Redis import Redis
from ...utils.dataUtil import switch_time
from flask import current_app as app
from manage import db


@select.route("/uploadFile", methods=["POST"])
def upload_files():
    files = request.files
    form = request.form
    file_list = files.getlist('file')
    print(file_list)
    li = []
    for file in file_list:
        upload_file = {}
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, keep_default_na=False, header=None)
            upload_file['name'] = file.filename
            upload_file['file_list'] = data.values.tolist()
            # 行数
            data_count = data.shape[0]
            user_api_bhv = UserApiBhv(user_id=int(form.get('userId')), data_count=data_count, api_name="上传csv文件接口")
            db.session.add(user_api_bhv)
        else:
            columns = pd.read_excel(file, keep_default_na=False).columns
            dataValue = pd.read_excel(file, keep_default_na=False).values
            print(len(dataValue))
            upload_file['name'] = file.filename
            upload_file['file_list'] = []
            upload_file['file_list'].append(columns.to_list())
            for i in dataValue:
                upload_file['file_list'].append(i.tolist())
        li.append(upload_file)
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
    # 定义空数组，盛放连接中所有的表名
    table_name_all = []

    # 如果数据库类型是PG
    if str(conn_obj['sqlType']).lower() == 'postgresql':
        # 使用psycopg2库连接PG数据库
        conn = get_post_conn(conn_obj)
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

        # table_name_all = [{id: 0, name: 'db_mysql',isSelect: false}]
    print("所有表名的查询结果：", table_name_all)
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

    if str(conn_obj['sqlType']).lower() == 'postgresql':
        # 连接PG数据库
        postgres_engine = get_post_engine(conn_obj)
        # 执行sql
        data = pd.read_sql(
            "select * from information_schema.columns where table_schema='public' and table_name=%(name)s",
            con=postgres_engine, params={'name': conn_obj['tableName']})

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
    print("所有字段的查询结果：", column_all)
    return APIResponse(200, column_all).body()


@select.route("/allData", methods=["POST"])
def select_all_data():
    """
    查询指定数据库中某表的所有数据，采用分页实现
    limitCount：可选项，默认为100条
    其它属性为必选项
    {
        "userId": 1
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
    # 获取分页结果
    res = paging(select_obj)
    start = res[0]
    offset = res[1]
    cur.execute('SELECT * FROM {} as t LIMIT {} offset {};'.format(select_obj['tableName'], offset, start))
    data = cur.fetchall()
    close_con(conn, cur)
    return APIResponse(200, data).body()


@select.route("/addDataByColumn", methods=["POST"])
def select_all_table_column():
    """
    查询某张表中某个字段的所有数据带分页
    limitCount：可选项，默认为100条
    columnName: 当此参数不写或者为 [] 时，默认为所有字段
    其它属性为必选项
    {
        "tableName": "ncov_china",
        "columnName": ["city", "add_ensure"],
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
    obj = request.get_json()
    print(obj)
    conn = get_post_conn(obj)
    cur = conn.cursor()
    # 获取分页结果
    res = paging(obj)
    start = res[0]
    offset = res[1]
    sql = 'SELECT'
    if (not obj.__contains__('columnName')) or len(obj['columnName']) == 0:
        sql = sql + ' *'
    else:
        arr = obj['columnName']
        # 循环拼接字段名
        for i in arr:
            sql = (sql + ' {},').format(i)
        # 删除末尾的 ‘,’
        sql = sql.strip(',')
    # 拼接表名和分页查询的参数
    sql = (sql + ' FROM {} LIMIT {} offset {};').format(obj['tableName'], offset, start)
    print(sql)
    # 执行 sql
    cur.execute(sql)
    data = cur.fetchall()

    # 重写JSONEncoder，使它可以将decimal转化为float等类型转换...
    class Encoder(json.JSONEncoder):
        def default(self, obj_param):
            if isinstance(obj_param, Decimal):
                return float(obj_param)
            elif isinstance(obj_param, datetime.date()):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj_param, datetime.date):
                return obj_param.strftime("%Y-%m-%d")
            else:
                return json.JSONEncoder.default(self, obj_param)

    data_json = json.dumps(data, cls=Encoder)
    data_loads = json.loads(data_json)
    close_con(conn, cur)
    return APIResponse(200, data_loads).body()


@select.route("/selectDataByColumn", methods=["POST"])
def select_table_column(self):
    """
    查询某张表中某个字段的所有数据带分页
    limitCount：可选项，默认为100条
    columnName: 当此参数不写或者为 [] 时，默认为所有字段
    其它属性为必选项
    {
        "tableName": "ncov_china",
        "columnName": ["city", "add_ensure"],
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
    obj = request.get_json()
    conn = get_post_conn(obj)
    cur = conn.cursor()
    # 获取分页结果
    res = paging(obj)
    start = res[0]
    offset = res[1]
    sql = 'SELECT'
    if (not obj.__contains__('columnName')) or len(obj['columnName']) == 0:
        sql = sql + ' *'
    else:
        arr = obj['columnName']
        # 循环拼接字段名
        for i in arr:
            sql = (sql + ' {},').format(i)
        # 删除末尾的 ‘,’
        sql = sql.strip(',')
    # 拼接表名和分页查询的参数
    sql = (sql + ' FROM {} LIMIT {} offset {};').format(obj['tableName'], offset, start)
    print(sql)
    # 执行 sql
    cur.execute(sql)
    data = cur.fetchall()
    user_api_bhv = UserApiBhv(user_id=obj['userId'], data_count=len(data), api_name="上传csv文件接口")
    db.session.add(user_api_bhv)
    close_con(conn, cur)
    return APIResponse(200, data).body()


@select.route("/filterData", methods=["POST"])
def filter_data():
    """
    {
        "allDataListIndex": 0,
        "allColNameList": ["cls_cd", "dpt_cty_cd", "arrv_cty_cd", "arrv_airpt_cd", "dpt_airpt_cd", "flt_nbr", "sub_cls_cd","flt_seg_dpt_mm", "flt_seg_dpt_hh", "day_id"],
        "colNameList": [ "dpt_cty_cd", "flt_seg_dpt_hh", "day_id", "flt_seg_dpt_mm"]
    }
    :return:
    """
    app.logger.info(Redis.read('test'))
    app.logger.info('============================进入filter_data接口============================')
    start = time.time()
    obj = request.get_json()
    col_all = obj['allColNameList']
    col = obj['colNameList']
    data_all = all_data_list[obj['allDataListIndex']]
    # 将对应表的所有数据转换数据类型为 dataFrame 型
    all_df = pd.DataFrame.from_records(data_all, columns=col_all)
    # 将指定列取出，组成单独的 df
    data_df = all_df[col]
    # 如果 x 轴上的数据为时间类型，则将其进行转换 ---> pandas 中的 timestamp 类型
    if switch_time(data_df[col[0]][0]):
        # 此处必须用 copy() 操作，不然会出现警告提示
        data_df = data_df.copy()
        # 将 x 轴上的数据改为 pandas 中的 time 类型
        data_df[col[0]] = pd.to_datetime(data_df[col[0]], errors='coerce', infer_datetime_format=True,
                                         format='%Y-%m-%d')
        data_df = data_df.set_index(col[0], drop=False)
        target = data_df.resample('M').agg(FunType[obj['funType']].value)
        if FunType[obj['funType']].value == 'max' or FunType[obj['funType']].value == 'min':
            target.index.name = None
        target.sort_values([col[0]], inplace=True)
        res_pd_data = target
        if FunType[obj['funType']].value == 'max' or FunType[obj['funType']].value == 'min':
            res_pd_data.reset_index(inplace=False)
        else:
            res_pd_data.reset_index(inplace=True)
        res_pd_data[col[0]] = res_pd_data[col[0]].astype('string')
    else:
        # 如果不是时间类型，则继续进行分组运算
        grouped = data_df.groupby(by=col[0])
        res_pd_data = grouped.agg(FunType[obj['funType']].value)
        res_pd_data.reset_index(inplace=True)

    # 设置别名
    res_pd_data.columns = obj['aliasList']
    res_json_data = res_pd_data.to_json(orient='records')
    res_data = spjson.loads(res_json_data)
    app.logger.info('执行时间：' + str(time.time() - start))
    return APIResponse(200, res_data).body()


@select.route('/diData', methods=['POST'])
def get_dimensionality_indicator():
    """
    获取指定表的所有字段并划分成数字型和非数字型的形式返回
    {
        "tableName": "ncov_china",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }
    :return: 维度数组和指标数组
    """
    obj = request.get_json()
    # 维度数组
    dimensionality = []
    # 指标数组
    indicator = []
    in_id = 0
    di_id = 0
    if obj is None:
        file = request.files.getlist('file')[0]
        if os.path.splitext(file.filename)[-1] == '.csv':
            csv_data = pd.read_csv(file, keep_default_na=False, header=0)
            # 获取各列的数据类型
            series = csv_data.dtypes
            for index, value in series.iteritems():
                if ('int' in str(value)) or ('float' in str(value)):
                    indicator.append({
                        'id': in_id,
                        'name': str(index),
                        'dataType': str(value)
                    })
                    in_id += 1
                else:
                    dimensionality.append({
                        'id': di_id,
                        'name': str(index),
                        'dataType': str(value)
                    })
                    di_id += 1
        else:
            # 此处为 excel 文件的读取方法
            pass
    else:
        conn = get_post_conn(obj)
        cursor = conn.cursor()
        sql = """
            SELECT
                A.attname AS CO,
                concat_ws('', T.typname, SUBSTRING(format_type(A.atttypid, A.atttypmod) FROM '\(.*\)')) AS TYPE
            FROM
                pg_class AS C,
                pg_attribute AS A,
                pg_type AS T 
            WHERE
                C.relname = '{}'
                AND A.attnum > 0
                AND A.attrelid = C.oid 
                AND A.atttypid = T.oid
        """.format(obj['tableName'])
        cursor.execute(sql)
        data = cursor.fetchall()
        for tu in data:
            item = tu[1]
            if ('int' in item) or ('float' in item):
                indicator.append({
                    'id': in_id,
                    'name': tu[0],
                    'dataType': item
                })
                in_id += 1
            if ('varchar' in item) or ('char' in item):
                dimensionality.append({
                    'id': di_id,
                    'name': tu[0],
                    'dataType': item
                })
                di_id += 1
    data = {
        'dimensionality': dimensionality,
        'indicator': indicator
    }
    print(data)
    return APIResponse(200, data).body()


@select.route('/getChartData', methods=['POST'])
def get_chart_data():
    """
    图表数据初始化接口
    参数：数据库连接对象的基本信息   或者   一个文件对象
    columnName: 指定字段数据
    其它属性为必选项
    {
        "userId": 1,
        "tableName": "ncov_china",
        "columnName": ["city", "add_ensure"],
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }
    :return: 全局数据列表的索引值
    """
    Redis.write("test", "测试Redis", 120)
    start = time.time()
    obj = request.get_json()
    if obj is None:
        files = request.files
        form = request.form
        index = get_file_chart_data(files, form.get('userId'))
    else:
        index = get_sql_chart_data(obj, obj['userId'])
    end = time.time()
    print('执行时间:', end - start)
    app.logger.info('图表数据初始化接口的执行时间为:' + str((end - start)))
    return APIResponse(200, {'allDataListIndex': index}).body()
