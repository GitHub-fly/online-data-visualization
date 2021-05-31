"""
    项目的入口
"""
from app.main import create_app, db
from flask_script import Manager  # 管理项目的额外制定的一些命令
from flask_migrate import Migrate, MigrateCommand  # 管理数据库需要的脚本 追踪数据库变化的脚本
from app.common.APIException import exception

app = create_app("develop")  # 工厂函数模式选择

manager = Manager(app)  # 用 manage进行项目管理 代管 app
Migrate(app, db)  # 把 app 和 db 的信息绑定起来进行追踪
manager.add_command("db", MigrateCommand)  # 绑定额外的 db 命令


"""
python3 manage.py db init #初始化
python3 manage.py db migrate -m "init message" #提交变更
python3 manage.py db upgrade # 升级变更
python3 manage.py db downgrade # 降级变更
"""

# 注册蓝图，并指定其对应的前缀（url_prefix）
app.register_blueprint(exception, url_prefix='/error')

if __name__ == '__main__':
    manager.run()
