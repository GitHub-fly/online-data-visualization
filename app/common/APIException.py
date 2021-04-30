import json
from flask import Blueprint, Response, request, json, jsonify
from werkzeug.exceptions import HTTPException

exception = Blueprint('exception', __name__)


# class APIException(HTTPException):
#     code = 500
#     msg = 'sorry, we made a mistake (*￣︶￣)!'
#     error_code = 999
#
#     def __init__(self, msg=None, code=None, error_code=None,
#                  headers=None):
#         if code:
#             self.code = code
#         if error_code:
#             self.error_code = error_code
#         if msg:
#             self.msg = msg
#         super(APIException, self).__init__(msg, None)
#
#     def get_body(self, environ=None):
#         body = dict(
#             msg=self.msg,
#             error_code=self.error_code,
#             request=request.method + ' ' + self.get_url_no_param()
#         )
#         text = json.dumps(body)
#         return text
#
#     def get_headers(self, environ=None):
#         """Get a list of headers."""
#         return [('Content-Type', 'application/json')]
#
#     @staticmethod
#     def get_url_no_param():
#         full_path = str(request.full_path)
#         main_path = full_path.split('?')
#         return main_path[0]


# @exception.app_errorhandler(APIException)
# def handle_error(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


@exception.app_errorhandler(404)
def error_404(error):
    """这个handler可以catch住所有abort(404)以及找不到对应router的处理请求"""
    res = {"status": 404, "message": "404错误,找不到对应router"}
    return Response(json.dumps(res), mimetype='application/json')


@exception.app_errorhandler(405)
def error_405(error):
    """这个handler可以catch住所有abort(405)以及请求方式有误的请求"""
    res = {"status": 405, "message": "请求方式错误"}
    return Response(json.dumps(res), mimetype='application/json')


@exception.app_errorhandler(500)
def error_500(error):
    res = {"status": 500, "message": "内部系统错误"}
    return Response(json.dumps(res), mimetype='application/json')





