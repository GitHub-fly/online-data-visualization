import psycopg2

if __name__ == '__main__':
    air_conn = psycopg2.connect(database='postgres', user='postgres', password='123321', host='localhost', port=5433)
    # 获取游标
    air_cursor = air_conn.cursor()
    arr = ['RENAME 省 TO province', 'RENAME 省确诊 TO pro_ensure', 'RENAME 省治愈 TO pro_cure',
           'RENAME 省死亡 TO pro_die', 'RENAME 市 TO city', 'RENAME 新增确诊 TO add_ensure',
           'RENAME 新增治愈 TO add_cure', 'RENAME 新增死亡 TO add_die', 'RENAME 确诊 TO ensure',
           'RENAME 治愈 TO cure', 'RENAME 死亡 TO die', 'RENAME 日期 TO date']
    for i in arr:
        sql = 'ALTER TABLE public."nCov_china_0313" {};'.format(i)
        # 执行sql
        air_cursor.execute(sql)
    # 提交修改
    air_conn.commit()

    # air_cursor.execute('select * from public.sample_1k_flts')
    # data = air_cursor.fetchall()
    # print('+++++++++++++++++++++++++++++++++++')
    # print('共{}条数据'.format(len(data)))
    # a = 0
    # for i in data:
    #     a = a + 1
    #     print(a)
    #     print(i)
    # 关闭数据库连接
    air_cursor.close()
    air_conn.close()

