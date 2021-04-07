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


@select.route("/uploadfile", methods=["POST"])
def filelist1():
    files = request.files
    filelist = files.getlist('file')
    li = []
    for file in filelist:
        if os.path.splitext(file.filename)[-1] == '.csv':
            data = pd.read_csv(file, header=None)
            li = data.values.tolist()
        else:
            columns = pd.read_excel(file).columns
            rows = pd.read_excel(file).values
            li.append(columns)
            for i in rows:
                li.append(i)
    return APIResponse(200, li).body()
