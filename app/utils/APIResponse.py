"""
自定义的响应体对象
"""


class APIResponse:
    error = None
    msg = None
    data = None

    def __init__(self, error, data):
        self.error = error
        if error == 200:
            self.msg = 'Success'
        else:
            self.msg = 'Fail'
        self.data = data

    def body(self):
        body = {
            'code': self.error,
            'msg': self.msg,
            'data': self.data
        }
        return body
