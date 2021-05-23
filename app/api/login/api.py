import requests
from sqlalchemy.sql.functions import now

from app.utils.databaseUtil import get_post_conn, close_con
from . import login
from app.utils.APIResponse import APIResponse
from flask import request, redirect
from flask import current_app as app

client_id = "75bfbb55511431752d68"
client_secrets = "d8dc6368a486c01f77dba202d117c102e1a001f5"

access_token = ''


@login.route("/oauth/redirect", methods=["GET"])
def get_user_info():
    app.logger.info('============================进入get_user_info接口============================')
    global access_token
    # 接收GitHub返回的code
    code = request.args.get('code')
    app.logger.info(code)
    # 带参请求，获取token
    token_url = "https://github.com/login/oauth/access_token?client_id={}&client_secret={}&code={}".format(client_id,
                                                                                                           client_secrets,
                                                                                                           code)
    header = {
        "accept": "application/json"
    }
    res = requests.post(token_url, headers=header)
    if res.status_code == 200:
        res_dict = res.json()
        print(res_dict)
        access_token = res_dict["access_token"]
    else:
        app.logger.warning('错误：access_token请求失败！')
    # 拿到token，向API请求用户信息
    user_url = 'https://api.github.com/user'
    access_token = 'token {}'.format(access_token)
    app.logger.info("token：" + str(access_token))
    headers = {
        'accept': 'application/json',
        'Authorization': access_token
    }
    isLogin = 0
    res = requests.get(user_url, headers=headers)
    if res.status_code == 200:
        res_dict = res.json()
        app.logger.info(res_dict)
        isLogin = 1
        user_info = {
            "id": res_dict["id"],
            "nickName": res_dict["login"],
            "avatar": res_dict["avatar_url"],
            "isLogin": isLogin
        }
    else:
        user_info = None
        app.logger.warning('错误：user_info请求失败！', user_info)

    # 将用户信息写入数据库
    if user_info:
        status = add_user(user_info)
        if status["code"] == 20000:
            return redirect("http://online.xueni.top:9999/#/data?user=" + str(user_info["id"]))
        else:
            return redirect("http://online.xueni.top:9999/#/errPage")


def add_user(user_info):
    """
    将用户信息添加到数据库
    :param user_info:
    :return:
    """
    app.logger.info("=============将用户信息写入数据库=============")
    conn_obj = {
        "tableName": "t_user",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"

    }

    conn = get_post_conn(conn_obj)
    cursor = conn.cursor()
    sql = "INSERT INTO t_user(id, update_time, is_disabled, avatar, role, create_time, nickname, is_login) " \
          "VALUES ({}, {}, {}, {}, {}, {}, {}, {})" \
        .format(user_info["id"], now(), 0, "'" + user_info["avatar"] + "'", 1, now(),
                "'" + user_info["nickName"] + "'", user_info["isLogin"])
    # try:
    cursor.execute(sql)
    conn.commit()
    status = {
        "code": 20000,
        "message": "写入成功！"
    }
    # except:
    #     status = {
    #         "code": 20001,
    #         "message": "写入失败！"
    #     }
    app.logger.info(status["message"])
    close_con(conn, cursor)
    return status


@login.route("/selectUser", methods=["POST"])
def select_user():
    conn_obj = {
        "tableName": "t_user",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }
    obj = request.get_json()
    print(obj)
    user_id = obj["userId"]
    conn = get_post_conn(conn_obj)
    cursor = conn.cursor()
    sql = "SELECT id, avatar, nickname, is_login FROM T_user WHERE id={}".format(user_id)
    cursor.execute(sql)
    data = cursor.fetchall()[0]
    user_info = {"userId": data[0], "avatar": data[1], "nickName": data[2], "isLogin": data[3]}
    return APIResponse(200, user_info).body()
