from enum import Enum, unique


@unique
class FunType(Enum):
    SUM = 'sum'
    MEAN = 'mean',
    MAX = 'max'
    MIN = 'min'
    # 标准差
    STD = 'std'
    # 方差
    VAR = 'var'
    # 中位数
    MEDIAN = 'median'
    # 分组数量
    SIZE = 'size'
