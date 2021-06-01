import os
import re

from flask import request
from app.utils.APIResponse import APIResponse
from . import add
from ..select.api import select_table_column
from ...models import TRcord
from manage import db


def calculate(n1, n2, operator):
    '''
    :param n1: float
    :param n2: float
    :param operator: + - * /
    :return: float
    '''
    result = 0
    if operator == "+":
        result = n1 + n2
    if operator == "-":
        result = n1 - n2
    if operator == "*":
        result = n1 * n2
    if operator == "/":
        result = n1 / n2
    return result


# 判断是否是运算符，如果是返回True
def is_operator(e):
    '''
    :param e: str
    :return: bool
    '''
    opers = ['+', '-', '*', '/', '(', ')']
    return True if e in opers else False


# 将算式处理成列表，解决横杠是负数还是减号的问题
def formula_format(formula):
    # 去掉算式中的空格
    formula = re.sub(' ', '', formula)
    # 以 '横杠数字' 分割， 其中正则表达式：(\-\d+\.?\d*) 括号内：
    # \- 表示匹配横杠开头； \d+ 表示匹配数字1次或多次；\.?表示匹配小数点0次或1次;\d*表示匹配数字1次或多次。
    formula_list = [i for i in re.split('(\-\d+\.?\d*)', formula) if i]

    # 最终的算式列表
    final_formula = []
    for item in formula_list:
        # 第一个是以横杠开头的数字（包括小数）final_formula。即第一个是负数，横杠就不是减号
        if len(final_formula) == 0 and re.search('^\-\d+\.?\d*$', item):
            final_formula.append(item)
            continue

        if len(final_formula) > 0:
            # 如果final_formal最后一个元素是运算符['+', '-', '*', '/', '('], 则横杠数字不是负数
            if re.search('[\+\-\*\/\(]$', final_formula[-1]):
                final_formula.append(item)
                continue
        # 按照运算符分割开
        item_split = [i for i in re.split('([\+\-\*\/\(\)])', item) if i]
        final_formula += item_split
    return final_formula


def decision(tail_op, now_op):
    '''
    :param tail_op: 运算符栈的最后一个运算符
    :param now_op: 从算式列表取出的当前运算符
    :return: 1 代表弹栈运算，0 代表弹运算符栈最后一个元素， -1 表示入栈
    '''
    # 定义4种运算符级别
    rate1 = ['+', '-']
    rate2 = ['*', '/']
    rate3 = ['(']
    rate4 = [')']

    if tail_op in rate1:
        if now_op in rate2 or now_op in rate3:
            # 说明连续两个运算优先级不一样，需要入栈
            return -1
        else:
            return 1

    elif tail_op in rate2:
        if now_op in rate3:
            return -1
        else:
            return 1

    elif tail_op in rate3:
        if now_op in rate4:
            return 0  # ( 遇上 ) 需要弹出 (，丢掉 )
        else:
            return -1  # 只要栈顶元素为(，当前元素不是)都应入栈。
    else:
        return -1


def final_calc(formula_list):
    num_stack = []  # 数字栈
    op_stack = []  # 运算符栈
    for e in formula_list:
        operator = is_operator(e)
        if not operator:
            # 压入数字栈
            # 字符串转换为符点数
            if (isinstance(e, int) or isinstance(e, float)):
                num_stack.append(e)
            else:
                num_stack.append(float(e))
        else:
            # 如果是运算符
            while True:
                # 如果运算符栈等于0无条件入栈
                if len(op_stack) == 0:
                    op_stack.append(e)
                    break

                # decision 函数做决策
                tag = decision(op_stack[-1], e)
                if tag == -1:
                    # 如果是-1压入运算符栈进入下一次循环
                    op_stack.append(e)
                    break
                elif tag == 0:
                    # 如果是0弹出运算符栈内最后一个(, 丢掉当前)，进入下一次循环
                    op_stack.pop()
                    break
                elif tag == 1:
                    # 如果是1弹出运算符栈内最后两个元素，弹出数字栈最后两位元素。
                    op = op_stack.pop()
                    num2 = num_stack.pop()
                    num1 = num_stack.pop()
                    # 执行计算
                    # 计算之后压入数字栈
                    num_stack.append(calculate(num1, num2, op))
    # 处理大循环结束后 数字栈和运算符栈中可能还有元素 的情况
    while len(op_stack) != 0:
        op = op_stack.pop()
        num2 = num_stack.pop()
        num1 = num_stack.pop()
        num_stack.append(calculate(num1, num2, op))

    return num_stack, op_stack


@add.route('/addNewColumn', methods=['POST'])
def add_new_table_column():
    obj = request.get_json()
    column_arr = {'sqlType': obj['sqlType'], 'userName': obj['userName'], 'password': obj['password'],
                  'host': obj['host'],
                  'port': obj['port'], 'database': obj['database'], 'limitCount': obj['limitCount'],
                  'columnName': obj['columnName'],
                  'tableName': obj['tableName'],
                  'page': obj['page']
                  }
    print(column_arr)
    formula = []
    res_list = []
    operate_list = ['+', '-', '*', '/', '(', ')']
    result_list = select_table_column(column_arr)['data']
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>数组数据", result_list)
    for item in result_list:
        character = []
        i = 0
        for element in obj['operatecontent']:
            if element in operate_list:
                character.append(element)
            else:
                character.append(item[i])
                i += 1
        str = ''.join('%s' % a for a in character)
        formula.append(str)
    for formula_list in formula:
        formu = formula_format(formula_list)
        result, _ = final_calc(formu)
        res = result[0]
        res_list.append(res)
    print(res_list)
    return APIResponse(200, res_list).body()


@add.route("/addUserBehavior", methods=['POST'])
def add_user_behavior():
    obj = request.files
    form = request.form
    file_list = obj.getlist('file')
    folder_name = form.get('folderName')
    parentId =0
    file_type = 0
    t_record = TRcord(name=folder_name)
    li = t_record.query.filter_by(name=folder_name,user_id = int(form.get("userId"))).all()
    if len(li) == 0:
        t_record = TRcord(user_id=int(form.get("userId")), name=folder_name, parent_id=1, upload_type=0)
        db.session.add(t_record)
    else:
        for item in li:
            if(item.name == folder_name):
                parentId = item.id
    if(parentId != 0):
        for file in file_list:
            if os.path.splitext(file.filename)[-1] == '.csv':
                file_type = 1
                t_record = TRcord(user_id=int(form.get("userId")), name=file.filename, parent_id=parentId, upload_type=file_type)
                db.session.add(t_record)
            else:
                file_type = 2
                t_record = TRcord(user_id=int(form.get("userId")), name=file.filename, parent_id=parentId, upload_type=file_type)
                db.session.add(t_record)
    return APIResponse(200, '成功').body()
