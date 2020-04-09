# 用作启动容器用的脚本
import multiprocessing
import os

bind = "0.0.0.0:8000"
#
# app_port = os.environ.get('APP_PORT') or 8000
# bind = bind.format(app_port)

workers = multiprocessing.cpu_count() * 2 + 1

# 运行脚本的方式
# gunicorn -c gunicorn.py manage:app

