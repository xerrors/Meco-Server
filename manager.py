from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db


# 初始化 migrate
# 两个参数一个是 Flask 的 app，一个是数据库 db
migrate = Migrate(app, db)

# 初始化管理器
manager = Manager(app)
# 添加 db 命令，并与 MigrateCommand 绑定
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
