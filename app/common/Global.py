"""
全局变量统一管理文件
"""
import threading

# 图表交互中所有数据列表
all_data_list = []

# 全局统一锁对象
lock = threading.Lock()
