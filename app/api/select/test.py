import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':

    airport_engine = create_engine('postgresql://postgres:root@localhost:5432/postgres')


# 获取的数据就是数据框的方式存放，很方便很后续的处理
# air_data = pd.read_sql(r"select * from pg_tables where schemaname='public'", con=airport_engine)
# print(air_data)
# air_data_o = air_data.head()
# tablename_ser = air_data["tablename"]
# print(tablename_ser)
