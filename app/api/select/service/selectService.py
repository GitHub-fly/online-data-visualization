import time
import os
import pandas as pd

from app.models import UserApiBhv
from app.utils.databaseUtil import close_con, get_post_conn
from pandas.io import json
from app.common.Global import all_data_list, lock
from manage import db
from app.utils.Redis import Redis
from flask import current_app as app


def fetchall_data(pool, obj, item, res_queue):
    """
    读取某张表中的所有数据方法
    :param pool:
    :param obj:
    :param item:
    :param res_queue:
    :return:
    """
    conn = pool.connection()
    cur = conn.cursor()
    sql = 'SELECT '
    if (not obj.__contains__('columnName')) or len(obj['columnName']) == 0:
        sql = sql + '*'
    else:
        sql = sql + ', '.join(obj['columnName'])
    # 拼接表名和分页查询的参数
    sql = (sql + ' FROM {} LIMIT {} OFFSET {};').format(obj['tableName'], item[1], item[0])
    # 执行 sql
    cur.execute(sql)
    time.sleep(0.1)
    data = cur.fetchall()
    res_queue.put(data)
    close_con(conn, cur)


def read_file_data(file_list: list, user_id):
    """
    读取文件数据方法
    :param file_list: 文件对象数组
    :param user_id: 用户 id
    :return:
    """
    file_data = []
    for file in file_list:
        upload_file = {}
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, keep_default_na=False)
            upload_file['name'] = file.filename
            upload_file['file_list'] = data.values.tolist()
            data_count = data.shape[0]
            user_api_bhv = UserApiBhv(user_id=user_id, data_count=data_count, api_name="数据分析接口")
            db.session.add(user_api_bhv)
        else:
            data = pd.read_excel(file, keep_default_na=False)
            columns = pd.read_excel(file, keep_default_na=False).columns
            rows = pd.read_excel(file, keep_default_na=False).values
            upload_file['name'] = file.filename
            upload_file['file_list'] = []
            upload_file['file_list'].append(columns.to_list())
            data_count = data.shape[0]
            user_api_bhv = UserApiBhv(user_id=user_id, data_count=data_count, api_name="数据分析接口")
            db.session.add(user_api_bhv)
            for i in rows:
                upload_file['file_list'].append(i.tolist())
        file_data.append(upload_file)

    return file_data


def get_sql_chart_data(obj, user_id):
    """
    获取数据库表中的所有数据
    :param obj:
    :param user_id:
    :return:
    """
    conn = get_post_conn(obj)
    cur = conn.cursor()
    sql = 'SELECT '
    if (not obj.__contains__('columnName')) or len(obj['columnName']) == 0:
        sql = sql + '*'
    else:
        sql = sql + ', '.join(obj['columnName'])
    # 拼接表名和分页查询的参数
    sql = (sql + ' FROM {};').format(obj['tableName'])
    cur.execute(sql)
    data = cur.fetchall()
    user_api_bhv = UserApiBhv(user_id=user_id, data_count=len(data), api_name="数据分析接口")
    db.session.add(user_api_bhv)
    cur.close()
    conn.close()
    """
    1. 全局变量存储方式
    """
    # 上锁开始在全局数组内追加数据
    # lock.acquire()
    # index = len(all_data_list)
    # all_data_list.append(data)
    # lock.release()
    """
    2. 整合 Redis 缓存
    """
    if Redis.is_exist(str(obj)):
        app.logger.warning('目标数据已存在=================直接拿取缓存中的数据')
        return str(obj)
    else:
        app.logger.info('存入redis ----------> ' + str(obj))
        Redis.write(str(obj), data)
        return str(obj)


def get_file_chart_data(files, user_id):
    """
    获取 csv 等文件数据
    :param files:
    :param user_id:
    :return:
    """
    file_list = files.getlist('file')
    file_obj_list = read_file_data(file_list, user_id)
    # 每个字段的数据存放在 column_data 内部，形式：['1', '7864']
    column_data = file_obj_list[0]['file_list']
    """
    1. 全局变量存储方式
    """
    # 上锁开始在全局数组内追加数据
    # lock.acquire()
    # index = len(all_data_list)
    # all_data_list.append(column_data)
    # lock.release()
    """
    2. 整合 Redis 缓存
    """
    if Redis.is_exist(str(file_list[0])):
        app.logger.warning('指定的 key 已存在')
        return str(file_list[0])
    else:
        app.logger.info('存入redis ----------> ' + str(file_list[0]))
        Redis.write(str(file_list[0]), column_data)
        return str(file_list[0])


def filter_sql(obj):
    """
    数据库表的分析处理方法
    :param obj:
    :return:
    """
    col_all = obj['allColNameList']
    col = obj['colNameList']
    data_all = all_data_list[obj['allDataListIndex']]
    # 将对应表的所有数据转换数据类型为dataFrame型
    df = pd.DataFrame.from_records(data_all, columns=col_all)
    # 将指定列取出，组成单独的df
    data = df[col]

    # 将数值型列和非数值型列分别存放（只存放列名）
    num_col_list = []
    not_num_list = []
    time_list = []
    # 判断每个列的类型
    for i in col:
        # 找出每列第一个非空值
        ids = data[i].first_valid_index()
        first_valid_value = data[i][ids]
        # 判断时间类型预处理
        pattern = ('%Y/%m/%d', '%Y-%m-%d', '%Y_%m_%d', '%y/%m/%d', '%y-%m-%d')
        for j in pattern:
            try:
                res = time.strptime(first_valid_value, j)
                if res:
                    # 将此值obj型转成datetime型
                    first_valid_value = pd.to_datetime(first_valid_value)
                    break
            except:
                continue
        # 查看类型
        value_type = str(type(first_valid_value))
        if ('int' in value_type) or ('float' in value_type):
            num_col_list.append(i)
        elif 'time' in value_type:
            time_list.append(i)
        else:
            not_num_list.append(i)
    # 根据维度的类型做不同聚合处理
    if (col[0] in num_col_list) or (col[0] in not_num_list):
        print('维度为数值型或字符型')
        data_filter = data.groupby(col[0]).agg('sum', numeric_only=True)
        data_filter_sort = data_filter.sort_values([col[0]], ascending=True)
        data_filter_sort.reset_index(inplace=True)
    elif col[0] in time_list:
        print('维度为时间型')
        data = data.copy()
        data[col[0]] = pd.to_datetime(data[col[0]], errors='coerce', infer_datetime_format=True,
                                      format='%Y-%m-%d')
        data = data.set_index(col[0], drop=False)
        # 以年、月、周为单位，聚合数据，并做简单计算：max、min、mean...
        target = data.resample('D').agg('sum')
        target.sort_values([col[0]], inplace=True)
        data_filter_sort = target
        data_filter_sort.reset_index(inplace=True)
        data_filter_sort[col[0]] = data_filter_sort[col[0]].astype('string')
    else:
        print('错误：无法识别维度类型！')
    df_json = data_filter_sort.to_json(orient='records')
    data_json = json.loads(df_json)
    return data_json
