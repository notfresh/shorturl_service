FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
RUN pip install pip -U  # update pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt


ADD . /code/ # copy the source code file to  code directory


