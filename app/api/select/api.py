from . import select  # . 表示同目录层级下
from app.models import Tb_1
from app.utils.APIResponse import APIResponse
from flask import request
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
