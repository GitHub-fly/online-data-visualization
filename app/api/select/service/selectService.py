import time


from app.utils.databaseUtil import close_con, get_post_conn


def fetchall_data(pool, obj, item, res_queue):
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
