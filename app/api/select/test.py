import time

from app.utils.databaseUtil import get_post_conn, close_con, paging
from time import strptime
import pandas as pd

if __name__ == '__main__':
    """
    columnName可以传数组，第一个值，必须传维度字段
    dimensionMode: "W" 或者 "M" 或者 "Y" ，以周或月或年为单位聚合数据
    targetMode："max"或"sum"或"mean", 计算指标的最大值，或求和，或平均值
    """
    # df显示设置
    start = time.time()
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
           "targetMode": "sum"}
    conn = get_post_conn(obj)
    col = obj['columnName']

    # 将传过来的columnName拼接为字符串，用作被查询的列名
    tag = ','
    select_column = tag.join(col)
    # 构造sql语句
    sql = "SELECT {} FROM {};".format(select_column, obj['tableName'])
    # 执行sql
    data = pd.read_sql(sql, conn)

    # 获取到第一个字段的类型
    s_dtype = str(data[col[0]].dtype)

    # 判断数值类型
    if ('int' in s_dtype) or ('float' in s_dtype):
        print('维度需要字符型数据！（当前维度为数值型）')
    else:
        # 随机获取1条数据判断类型
        data_sp = data[col[0]].sample(1)
        if data_sp.notna:
            # 将字符串尝试转换为这几种常见的日期形式，转换成功则是日期型
            pattern = ('%Y_%m_%d', '%Y/%m/%d', '%Y-%m-%d', '%y年%m月%d日', '%y-%m-%d')
            for i in pattern:
                try:
                    res = strptime(data_sp.iat[0], i)
                    if res:
                        data[col[0]] = pd.to_datetime(data[col[0]])
                except:
                    continue
            if 'datetime' in str(data[col[0]].dtype):
                print('按日期聚合')
                # 设置日期为当前df对象的索引
                data = data.set_index(data[col[0]], drop=False)
                # 以年、月、周为单位，聚合数据，并做简单计算：max、min、mean...
                target = data.resample(obj['dimensionMode']).agg(obj["targetMode"])
                target_sort = target.sort_index()
                print(target_sort)
            else:
                # 按字符聚合
                print('按字符聚合')
                data_filter = data.groupby(col[0]).agg([obj['targetMode']], numeric_only=True)
                data_filter_sort = data_filter.sort_values([col[0]], ascending=True)
                print(data_filter_sort)

    # # 将时间列的datetime型转为string型
    # target[columnName[0]] = target[columnName[0]].astype('string')
    # 将dataframe类型转为json返回给前端
    # df_json = target.to_json(orient='records')
    # df_json_load = json.loads(df_json)
    # for i in df_json_load:
    #     print(i)
