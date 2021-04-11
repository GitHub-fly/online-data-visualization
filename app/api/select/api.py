from . import select  # . 表示同目录层级下
from app.models import Tb_1
from app.utils.APIResponse import APIResponse
from sqlalchemy import create_engine
import psycopg2
import xlrd
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os


@select.route("/test", methods=["GET"])
def test():
    tb = Tb_1.query.get(2).tb_1_dict()
    res = APIResponse(200, tb)
    return res.body()


@select.route("/uploadFile", methods=["POST"])
def upload_file():
    files = request.files
    file_list = files.getlist('file')
    li = []
    for file in file_list:
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, keep_default_na=False, header=None)
            li = data.values.tolist()
        else:
            columns = pd.read_excel(file, keep_default_na=False).columns
            rows = pd.read_excel(file, keep_default_na=False).values
            li.append(columns.to_list())
            print(type(rows))
            for i in rows:
                li.append(i.tolist())
    return APIResponse(200, li).body()


@select.route("/selectAllTable", methods=["POST"])
def select_all_table():
    # 获取前端传来的连接对象
    conn_obj = request.get_json()
    print(conn_obj)
    # 使用psycopg2库连接
    air_conn = psycopg2.connect(database=conn_obj['sqlType'], user=conn_obj['userName'], password=conn_obj['password'],
                                host=conn_obj['host'], port=conn_obj['port'])
    # 获取游标
    air_cursor = air_conn.cursor()
    # 执行sql
    air_cursor.execute("select * from pg_tables where schemaname = 'public'")
    # 接收返回结果集
    data = air_cursor.fetchall()
    # 关闭数据库连接
    air_conn.close

    # 定义空数组，盛放连接中所有的表名
    tablename_all = []
    # 循环结果集（结果集格式为列表套元组）
    for d in data:
        # 将元组中需要的元素 => 表名，组成新的列表
        tablename_all.append(d[1])
    return APIResponse(200, tablename_all).body()


@select.route("/selectAllColumn", methods=["Get"])
def select_all_column():
    return APIResponse(200, 'all').body()
