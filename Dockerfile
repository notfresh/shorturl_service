FROM python:3.6

ENV PYTHONUNBUFFERED 1

# 添加 Debian 清华镜像源
RUN echo \
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free\
    > /etc/apt/sources.list

RUN mkdir /code
WORKDIR /code
RUN pip install pip -U  -i https://pypi.tuna.tsinghua.edu.cn/simple  # update pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


ADD . /code/ # copy the source code file to  code directory


