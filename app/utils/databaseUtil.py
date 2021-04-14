import psycopg2


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

