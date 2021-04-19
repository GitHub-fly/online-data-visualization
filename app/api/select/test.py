from app.utils.databaseUtil import get_post_conn, close_con, paging
import pandas as pd
import json

if __name__ == '__main__':
    """
    columnName可以传数组，第一个值，必须传维度字段
    dimensionMode: "W" 或者 "M" 或者 "Y" ，以周或月或年为单位聚合数据
    targetMode："max"或"sum"或"mean", 计算指标的最大值，或求和，或平均值
    """
    # df显示设置
    pd.set_option('display.max_colwidth', 1000)  # 最大列宽
    pd.set_option('display.width', 10000)  #
    pd.set_option('display.min_rows', 1000)  #

    obj = {"tableName": "sample_1k_flts",
           "columnName": ["day_id", "pax_qty", "net_amt"],
           "sqlType": "postgresql",
           "userName": "postgres",
           "password": "root",
           "host": "localhost",
           "port": "5432",
           "database": "postgres",
           "dimensionMode": "W",
           "targetMode": "max"}
    conn = get_post_conn(obj)
    columnName = obj['columnName']
    # 将传过来的columnName拼接为字符串，用作被查询的列名
    tag = ','
    select_column = tag.join(columnName)
    # 构造sql语句
    sql = "SELECT {} FROM {};".format(select_column, obj['tableName'])
    # 执行sql
    data = pd.read_sql(sql, conn)
    # 将df中类型为时间的列转为datetime型
    data[columnName[0]] = pd.to_datetime(data[columnName[0]], format='%Y/%m/%d')
    # 设置日期为当前df对象的索引
    data = data.set_index(data[columnName[0]], drop=False)
    # 以年、月、周为单位，聚合数据，并做简单计算：max、min、mean...
    target = data.resample(obj['dimensionMode']).agg(obj["targetMode"])
    # 将时间列的datetime型转为string型
    target[columnName[0]] = target[columnName[0]].astype('string')
    # 将dataframe类型转为json返回给前端
    df_json = target.to_json(orient='records')
    df_json_load = json.loads(df_json)
    for i in df_json_load:
        print(i)

