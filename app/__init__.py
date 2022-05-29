# -*- coding:utf-8 -*-
import os
import random

from flask import Flask, render_template, flash
from flask_wtf import Form
from flask_bootstrap import Bootstrap
from flask_redis import FlaskRedis

from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Length

from config import CONFIGS

import sqlalchemy as sa
from .models import ShortURL, db, User

app = Flask(__name__)

# redis_client = FlaskRedis()


def create_app(flask_config='development', **kwargs):
    config_name = os.getenv('FLASK_ENV', flask_config)
    app.config.from_object(CONFIGS[config_name])
    app.config['SECRET_KEY'] = 'so easy you are'
    from . import models # 创建表
    from . import errorhandlers
    errorhandlers.init_app(app)
    from . import db
    db.init_app(app)
    bootstrap = Bootstrap(app)
    # redis_client.init_app(app)
    return app


class TheForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    customize_url = StringField("you can assgin a short name if you like", validators=[Length(min=2, max=16)])
    submit = SubmitField("shorten")

class DeleteForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    customize_url = StringField("you can assgin a short name if you like", validators=[Length(min=2, max=16)])
    submit = SubmitField("shorten")


def rehash_baseh62(the_url_str):
    ls = [str(item) for item in range(10)]

    for item in range(65, 91):
        ls.append(chr(item))

    for item in range(97, 123):
        ls.append(chr(item))

    res = []
    import mmh3
    num = mmh3.hash(the_url_str, signed=False)
    while num:
        res.insert(0, ls[num%62])
        num = num // 62

    return ''.join(res)


@app.route('/', methods=['POST', 'GET'])
def index():
    default_shorten_url = 'Default random'
    form = TheForm(customize_url=default_shorten_url)
    urls = ShortURL.query.all()
    if form.validate_on_submit():

        the_url = form.the_url.data
        customize_url = form.customize_url.data
        full_shorten_url = ''
        while True:
            if customize_url == default_shorten_url:
                shorten_url = rehash_baseh62(the_url)  #压缩算法或者自定义短网址，本系统的核心
            # 查询这个网址有没有被压缩
            # saved_shorten_url = ShortURL.query.filter_by(origin_url)
            else:
                shorten_url = customize_url
            url = ShortURL(origin_url=the_url, shorten_url=shorten_url)
            # 保存
            try:
                # 试探着保存,如果保存成功, 那么跳出循环
                # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.add(url)
                db.session.commit()
                break
            except sa.exc.IntegrityError as e:
                db.session.rollback()
                saved_origin_url = db.session.query(ShortURL.origin_url).filter_by(shorten_url=shorten_url).first()
                # print(shorten_url + " exists, roll back")
                # 自定义短网址命名重复
                if customize_url != default_shorten_url:
                    flash('the assgined name has been taken before')
                    return render_template('index.html', form=form,
                                           shorten_url=make_full_url(app, shorten_url),
                                           taken=True,
                                           took_url=saved_origin_url[0])
                # 没有采用自定义网址, 默认采用压缩的方式, 但是之前已经存储过 或者 压缩的时候哈希冲突
                if customize_url == default_shorten_url:
                    # 之前已经存储过, 不做处理
                    if saved_origin_url[0] == the_url:
                        print("the url has been hash shortened")
                        break
                    # 压缩的时候哈希冲突，概率极小, 做进一步处理
                    else:
                        # 网址里面有附加参数
                        if '?' in the_url:
                            the_url += ('&randomk=' + str(random.random()))
                        else:
                            if the_url[-1] != '/':  # 没有以/结尾
                                the_url += '/'
                            the_url += ('?randomk=' + str(random.random()))
            except Exception as e:
                return render_template('500.html'), 500
        return render_template('index.html', form=form, shorten_url=make_full_url(app, shorten_url), urls=urls)
    return render_template('index.html', form=form,urls=urls)

# @app.route("/delete", methods="POST")
# def delete_short_url(shorten_url):
#     pass



def make_full_url(app, shorten_url):
    DOMAIN_NAME = app.config['DOMAIN_NAME']
    PORT = app.config['PORT']
    HTTP = app.config['HTTP']
    if PORT == 80:
        full_shorten_url = '{http}://{domain_name}/{short_url}'.format(http=HTTP, domain_name=DOMAIN_NAME, port=PORT, short_url=shorten_url)
    else:
        full_shorten_url = '{http}://{domain_name}:{port}/{short_url}'.format(http=HTTP, domain_name=DOMAIN_NAME, port=PORT, short_url=shorten_url)
    return full_shorten_url


@app.route('/<string:short_url>', methods=['GET'])
def redirect_short_url(short_url):
    url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    return redirect(url.origin_url)
    # origin_url = redis_client.get(short_url)
    # if not origin_url:
    #     url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    #     origin_url = url.origin_url
    #     redis_client.set(short_url, origin_url, 24*3600)
    # return redirect(origin_url)


@app.route('/<string:short_url_prefix>/<string:short_url>', methods=['GET'])
def redirect_short_url_with_prefix(short_url, short_url_prefix):
    # origin_url = redis_client.get(short_url_prefix + '/' + short_url)
    # if not origin_url:
    url = ShortURL.query.filter_by(shorten_url=short_url_prefix + '/' + short_url).first_or_404()
    origin_url = url.origin_url
    # redis_client.set(short_url_prefix + '/' + short_url, origin_url, 24*3600)
    return redirect(origin_url)


@app.route('/about')
def about():
    return render_template('about.html')







