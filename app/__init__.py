# -*- coding:utf-8 -*-
import os
from flask import Flask, render_template
from flask_wtf import Form
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


from config import CONFIGS
from flask_bootstrap import Bootstrap

import sqlalchemy as sa
from .models import ShortURL, db

app = Flask(__name__)


def create_app(flask_config='development', **kwargs):
    config_name = os.getenv('FLASK_ENV', flask_config)
    app.config.from_object(CONFIGS[config_name])
    app.config['SECRET_KEY'] = 'so easy you are'
    from . import models # 创建表

    from . import errorhandlers
    errorhandlers.init_app(app)

    from . import modules
    modules.init_app(app)

    from . import db
    db.init_app(app)

    bootstrap = Bootstrap(app)

    return app


class TheForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    submit = SubmitField("shorten")


@app.route('/', methods=['POST', 'GET'])
def index():
    form = TheForm()
    if form.validate_on_submit():

        the_url = form.the_url.data
        import random

        while True:
            shorten_url = random.randint(1, 10000) # 压缩算法或者自定义短网址，本系统的核心，TODO

            # 查询这个网址有没有被压缩
            # saved_shorten_url = ShortURL.query.filter_by(origin_url)

            url = ShortURL(origin_url=the_url, shorten_url=shorten_url)

            # 保存
            try:
                db.session.add(url) # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.commit()
                break
            except sa.exc.IntegrityError as e:
                db.session.rollback()
                print(shorten_url + " exists, roll back")
        DOMAIN_NAME = app.config['DOMAIN_NAME']
        PORT = app.config['PORT']
        HTTP = app.config['HTTP']
        full_shorten_url = '{http}://{domain_name}:{port}/{short_url}'.format(http=HTTP, domain_name=DOMAIN_NAME, port=PORT, short_url=shorten_url)
        return render_template('index.html', form=form, shorten_url=full_shorten_url)

    return render_template('index.html', form=form)


@app.route('/<string:short_url>', methods=['GET'])
def redirect_short_url(short_url):
    url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    return redirect(url.origin_url)
    # return '你好'





