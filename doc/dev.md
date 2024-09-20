# Intro
## 如何测试？
1. 安装虚拟环境，python -m venv venv。
2. 激活虚拟环境并且安装依赖。 
```
source vev/bin/activate
pip install -r requirements
```
3. 启动服务。
```
python manage.py runserver -p 8080 -h 0.0.0.0
```


# 版本管理
## flask升级的问题
老的flask的send_file有一个参数叫 attachment_filename, 高版本的叫 download_name 

# 更新记录
1. 现在已经增加下载功能，可以把自己保存的短网址批量全部下载下来。
