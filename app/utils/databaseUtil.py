import psycopg2
import pandas as pd


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
    if hasattr(conn_obj, 'limitCount'):
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