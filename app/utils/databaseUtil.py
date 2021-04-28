import time

import psycopg2
import pandas as pd
from dbutils.pooled_db import PooledDB
from sqlalchemy import create_engine


def get_post_conn(obj):
    """
    获取 postgres 数据库的连接对象
    :param obj: 连接参数对象
    :return: 连接对象
    """
    conn = psycopg2.connect('{}://{}:{}@{}:{}/{}'.format(
        str(obj['sqlType']).lower(), obj['userName'], obj['password'], obj['host'],
        obj['port'], obj['database']
    ))
    return conn


def get_post_engine(obj):
    return create_engine('{}://{}:{}@{}:{}/{}'.format(
        str(obj['sqlType']).lower(), obj['userName'], obj['password'], obj['host'],
        obj['port'], obj['database']
    ))

def pool_post_conn(obj):
    """
    获取 postgres 数据库的连接对象，采用数据连接池技术
    :param obj: 连接参数对象
    :return: 连接池对象
    """
    pool = PooledDB(psycopg2,  # 使用连接数据库的模块 psycopg2
                    3,  # 最低预启动数据库连接数量
                    maxconnections=120,  # 连接池允许的最大连接数，0 和 None 表示不限制连接数
                    host=obj['host'],
                    user=obj['userName'],
                    password=obj['password'],
                    port=obj['port'],
                    database=obj['database'])
    return pool


def close_con(conn, cursor):
    """
    关闭数据库的连接和指针的连接
    :param conn: 数据库连接对象
    :param cursor: 指针对象
    :return:
    """
    cursor.close()
    conn.close()


def paging(conn_obj):
    """
    将前端传递过来的对象进行分页处理
    :param conn_obj: 前端传递过来的连接对象等信息
    :return: 分页的起始点和查询条数
    """
    # 第几页
    page = conn_obj['page'] - 1
    limit_count = 100
    # 判断前端传递过来的参数中是否含有 'limitCount'
    if conn_obj.__contains__('limitCount'):
        # 每页多少条数据
        limit_count = conn_obj['limitCount']
    # 开始查询的起点
    start = page * limit_count
    return start, limit_count


def display_df():
    # df显示设置
    pd.set_option('display.max_colwidth', 1000)  # 最大列宽
    pd.set_option('display.width', 10000)  #
    pd.set_option('display.min_rows', 1000)  #


def get_page_size(obj, queue_size):
    """
    获取分页参数方法
    :param obj: 连接参数对象
    :param queue_size: 消息队列的限制个数
    :return: [[0, 45959], [45959, 45959], [91918, 45959], [137877, 45959], [183836, 45959]]
    """
    start = time.time()
    conn = get_post_conn(obj)
    sql = "SELECT COUNT(1) FROM sample_1k_flts"
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    print('查询条数所花时间：', time.time() - start)
    close_con(conn, cur)
    # 数据行数
    count = data[0][0]
    offset = int(count / queue_size + 0.5)
    # 分页参数数组
    arr = []
    for page in range(queue_size):
        arr.append(
            [page * offset, offset]
        )
    return arr
