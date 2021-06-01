import requests
from sqlalchemy.sql.functions import now

from app.models import TUser
import app.models as md
from app.utils.databaseUtil import get_post_conn, close_con, get_post_engine
from . import login
from app.utils.APIResponse import APIResponse
from flask import request, redirect, Flask
from flask import current_app as app
from manage import db

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
    try:
        res = requests.post(token_url, headers=header, timeout=10)
    except:
        return "第三方登录超时，请重新登录！"
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
    res = requests.get(user_url, headers=headers)
    # 构造用户对象
    if res.status_code == 200:
        res_dict = res.json()
        app.logger.info(res_dict)
        isLogin = 1
        user_info = {
            "nickName": res_dict["login"],
            "account": res_dict["login"],
            "avatar": res_dict["avatar_url"],
            "isLogin": isLogin,
            "password": 123123,
            "roleId": 1,
            "isDisabled": 1,
            "openId": res_dict["id"]
        }
    else:
        user_info = None
        app.logger.warning('错误：user_info请求失败！', user_info)
    app.logger.info(user_info)

    # 将用户信息写入数据库
    if user_info:
        status = add_user(user_info)
        app.logger.info(status)
        if status["code"] == 20000:
            return redirect("http://localhost:9999/#/data?user=" + str(user_info["openId"]))
        else:
            return redirect("http://localhost:9999/#/errPage")


# @login.route("/adduser", methods=["GET"])
def add_user(user_info):
    """
    将用户信息添加到数据库
    :param user_info:
    :return:
    """
    app.logger.info("=============将用户信息写入数据库=============")

    try:
        obj = md.TUser.query.filter_by(open_id=user_info["openId"]).first()
        if obj is not None:
            status = {
                "code": 20000,
                "message": "存在用户，拒绝重复写入！"
            }
            return status
        else:
            t_user = TUser(account=user_info["account"], password=user_info["password"], nickname=user_info["nickName"],
                           avatar=user_info["avatar"], is_login=user_info["isLogin"], role_id=user_info["roleId"],
                           is_disabled=user_info["isDisabled"], open_id=user_info["openId"])
            db.session.add(t_user)
            status = {
                "code": 20000,
                "message": "写入成功！"
            }
    except Exception as e:
        print(e)
        status = {
            "code": 20001,
            "message": "写入失败！"
        }
    app.logger.info(status["message"])
    return status


@login.route("/selectUser", methods=["POST"])
def select_user():
    obj = request.get_json()
    print(obj)
    open_id = obj["openId"]
    obj = md.TUser.query.filter_by(open_id=open_id).first()
    data = obj.json_data()
    print(data)
    return APIResponse(200, data).body()
