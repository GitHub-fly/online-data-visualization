import psycopg2

conn = psycopg2.connect(database='postgres', user='postgres', password='root', host='localhost', port=5432)
cursor = conn.cursor()


def close_con(a, b):
    """
    关闭数据库的连接和指针的连接
    :param a: 数据库连接对象
    :param b: 指针对象
    :return:
    """
    a.close()
    b.close()


def table_rename():
    """
    修改表名
    如果表名中出现大小写，必须使用：public."xXXX" 方式来定义表名
    所以建议所有的表名都改为小写字母
    :return:
    """
    cursor.execute('ALTER TABLE public."nCov_china_0313" RENAME TO ncov_chain')
    conn.commit()
    close_con(conn, cursor)


def column_rename():
    """
    修改字段名称
    :return:
    """
    arr = ['RENAME 省 TO province', 'RENAME 省确诊 TO pro_ensure', 'RENAME 省治愈 TO pro_cure',
           'RENAME 省死亡 TO pro_die', 'RENAME 市 TO city', 'RENAME 新增确诊 TO add_ensure',
           'RENAME 新增治愈 TO add_cure', 'RENAME 新增死亡 TO add_die', 'RENAME 确诊 TO ensure',
           'RENAME 治愈 TO cure', 'RENAME 死亡 TO die', 'RENAME 日期 TO date']
    for i in arr:
        sql = 'ALTER TABLE ncov_china {};'.format(i)
        # 执行sql
        cursor.execute(sql)
    # 提交修改
    conn.commit()
    close_con(conn, cursor)


if __name__ == '__main__':
    table_rename()

