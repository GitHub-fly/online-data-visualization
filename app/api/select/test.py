import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify

if __name__ == '__main__':
    # select_obj = {'tableName': 'article', 'sqlType': 'postgresql', 'userName': 'postgres', 'password': 'root',
    #               'host': 'localhost', 'port': '5432', 'database': 'airfast'}
    select_obj = request.get_json()
    airport_engine = create_engine('{}://{}:{}@{}:{}/{}'.format(
        str(select_obj['sqlType']).lower(), select_obj['userName'], select_obj['password'], select_obj['host'],
        select_obj['port'], select_obj['database']
    ))

    # airport_engine_co = create_engine('postgresql://postgres:root@localhost:5432/postgres')
    data = pd.read_sql(
        "select * from information_schema.columns where table_schema='public' and table_name=%(name)s",
        con=airport_engine, params={'name': select_obj['tableName']})
    data_h = data.head()
    column_all = data_h['column_name']
    print(data)
    print(column_all.tolist())
