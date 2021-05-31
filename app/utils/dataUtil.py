import time


def switch_time(obj):
    """
    判断一个字符串转为能否转为 datetime 类型的时间
    :param obj:
    :return: 如果能：返回转换后的时间；如果不能，返回 原值
    """
    pattern = ('%Y/%m/%d', '%Y-%m-%d', '%Y_%m_%d', '%y/%m/%d', '%y-%m-%d')
    for j in pattern:
        # noinspection PyBroadException
        try:
            time.strptime(obj, j)
            return True
        except BaseException:
            return False


def get_data_type(obj):
    """
    判断一个对象的数据类型
    :param obj:
    :return:
    """
    value_type = str(type(obj))
    if 'int' in value_type:
        return int
    elif 'time' in value_type:
        return 'time'
    elif 'float' in value_type:
        return float
    else:
        return None
