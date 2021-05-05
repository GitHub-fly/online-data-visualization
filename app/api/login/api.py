import requests
from sqlalchemy.sql.functions import now

from app.utils.databaseUtil import get_post_conn, close_con
from . import login
from app.utils.APIResponse import APIResponse
from flask import request, redirect

client_id = "75bfbb55511431752d68"
client_secrets = "d8dc6368a486c01f77dba202d117c102e1a001f5"
global access_token


@login.route("/oauth/redirect", methods=["GET"])
def get_user_info():
    print('============================进入get_user_info接口============================')
    global access_token
    # 接收GitHub返回的code
    code = request.args.get('code')
    print('code：', code)
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
        access_token = res_dict["access_token"]
    else:
        print('错误：access_token请求失败！')
    # 拿到token，向API请求用户信息
    user_url = 'https://api.github.com/user'
    access_token = 'token {}'.format(access_token)
    print("token：", access_token)
    headers = {
        'accept': 'application/json',
        'Authorization': access_token
    }
    isLogin = 0
    res = requests.get(user_url, headers=headers)
    if res.status_code == 200:
        res_dict = res.json()
        print(res_dict)
        isLogin = 1
        user_info = {
            "id": res_dict["id"],
            "nickName": res_dict["login"],
            "avatar": res_dict["avatar_url"],
            "isLogin": isLogin
        }
        # 重定向回客户端
        redir('http://localhost:9999/#/data')
    else:
        user_info = None
        print('错误：user_info请求失败！', user_info)

    # 将用户信息写入数据库
    if user_info:
        add_user(user_info)
    return redirect('http://localhost:9999/#/data', 301)


def redir(re_url):
    """
    重定向回客户端
    :param re_url:
    :return:
    """
    print("=============重定向回客户端=============")
    return redirect(re_url, 301)


# @login.route("/adduser", methods=["GET"])
def add_user(user_info):
    """
    将用户信息添加到数据库
    :param user_info:
    :return:
    """
    print("=============将用户信息写入数据库=============")
    conn_obj = {
        "tableName": "t_user",
        "sqlType": "postgresql",
        "userName": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"

    }

    # user_info = {
    #     "id": "55419799",
    #     "nickName": "ycshang123",
    #     "avatar": "https://avatars.githubusercontent.com/u/55419799?v=4",
    #     "isLogin": 1
    # }
    conn = get_post_conn(conn_obj)
    cursor = conn.cursor()
    sql = "INSERT INTO t_user(id, update_time, is_disabled, avatar, role, create_time, nickname, is_login) " \
          "VALUES ({}, {}, {}, {}, {}, {}, {}, {})" \
        .format(user_info["id"], now(), 0, "'"+user_info["avatar"]+"'", 1, now(),
                "'"+user_info["nickName"]+"'", user_info["isLogin"])
    print(sql)
    cursor.execute(sql)
    conn.commit()
    close_con(conn, cursor)

    return APIResponse(200, 'add').body()
