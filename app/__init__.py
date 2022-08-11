# -*- coding:utf-8 -*-
import os
import random

from flask import Flask, render_template, flash, url_for
from flask_login import LoginManager, login_required
from flask_mail import Mail
from flask_wtf import Form
from flask_bootstrap import Bootstrap
from flask_redis import FlaskRedis
from flask_login import current_user
from flask_login import UserMixin, AnonymousUserMixin

from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, URL, Length

from config import CONFIGS

import sqlalchemy as sa
from .models import ShortURL, db, User

app = Flask(__name__)

# redis_client = FlaskRedis()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

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
    login_manager.init_app(app)
    mail.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser


class TheForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    customize_url = StringField("you can assgin a short name if you like", validators=[Length(min=2, max=16)])
    is_public = RadioField('whether you want to make the shorten url public', choices=[('True', 'Yes'), ('False', 'No')], default='False')
    submit = SubmitField("shorten")

class UpdateForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    customize_url = StringField("you can assgin a short name if you like", validators=[Length(min=2, max=16)])
    is_public = RadioField('whether you want to make the shorten url public', choices=[('True', 'Yes'), ('False', 'No')], default='False')
    submit = SubmitField("Update")

class DeleteForm(Form):
    the_url = StringField("the origin url to be shorten", render_kw={'readonly': True})
    customize_url = StringField("you can assgin a short name if you like",  render_kw={'readonly': True})
    confirm = StringField("enter yes to confirm", validators=[DataRequired()])
    submit = SubmitField("Delete")


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

def make_public(shorten_url, is_public):
    if shorten_url.startswith('p/'):
        return shorten_url
    if is_public == True:  # 一定要和True比较,否则会认为判断这个变量是否存在
        shorten_url = 'p/' + shorten_url
        print("################## public")
    print("################## public ??", is_public, shorten_url)
    return shorten_url

def clear_public(shorten_url):
    if shorten_url.startswith('p/'):
        return shorten_url[2:]
    return shorten_url

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    default_shorten_url = 'Default random'
    form = TheForm(customize_url=default_shorten_url)
    if current_user.is_authenticated:
        urls = ShortURL.query.filter_by(created_by=current_user.username).all()
    else:
        urls = []
    if form.validate_on_submit():
        the_url = form.the_url.data
        customize_url = form.customize_url.data
        is_public = form.is_public.data
        created_by = current_user.username
        while True:
            if customize_url == default_shorten_url:
                shorten_url = rehash_baseh62(the_url)  #压缩算法或者自定义短网址，本系统的核心
            else:
                shorten_url = make_public(customize_url, form.is_public.data == 'True')
            url = ShortURL(origin_url=the_url, shorten_url=shorten_url,created_by=created_by, is_public=is_public, shorten_url_created_by=shorten_url+"-"+str(created_by))
            # 保存
            try:
                # 试探着保存, 如果保存成功, 那么跳出循环
                # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.add(url)
                db.session.commit()
                break
            except sa.exc.IntegrityError as e:
                db.session.rollback()
                saved_origin_url = db.session.query(ShortURL.origin_url).filter_by(shorten_url=shorten_url, created_by=created_by).first()
                # print(shorten_url + " exists, roll back")
                # 自定义短网址命名重复
                if customize_url != default_shorten_url:
                    flash('the assgined name has been taken before')
                    took_url = saved_origin_url[0] # 第一个字段
                    return render_template('index.html', form=form,
                                           shorten_url=make_full_url(app, shorten_url),
                                           taken=True,
                                           took_url=took_url)
                # 没有采用自定义网址, 默认采用压缩的方式, 但是之前已经存储过 或者 压缩的时候哈希冲突
                if customize_url == default_shorten_url:
                    # 之前已经存储过, 不做处理
                    if saved_origin_url == the_url:
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
        return render_template('index.html', form=form, shorten_url=make_full_url(app, shorten_url, is_public), urls=urls)
    return render_template('index.html', form=form,urls=urls)

# @app.route("/delete", methods="POST")
# def delete_short_url(shorten_url):
#     pass


def make_full_url(app, shorten_url, is_public='False'):
    DOMAIN_NAME = app.config['DOMAIN_NAME']
    PORT = app.config['PORT']
    HTTP = app.config['HTTP']
    environ = app.config["ENVIRON"]
    if environ == "production":
        full_shorten_url = '{http}://{domain_name}/{short_url}'.format(http=HTTP, domain_name=DOMAIN_NAME, port=PORT, short_url=shorten_url)
    else:
        full_shorten_url = '{http}://{domain_name}:{port}/{short_url}'.format(http=HTTP, domain_name=DOMAIN_NAME, port=PORT, short_url=shorten_url)
    return full_shorten_url


@app.route('/p/<string:short_url>', methods=['GET'])
def redirect_public_short_url(short_url):
    short_url = "p/" + short_url
    url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    return redirect(url.origin_url)


@app.route('/detail/p/<string:short_url>', methods=['GET','POST'])
@login_required
def detail2Level(short_url):
    return detail("p/"+short_url)


# @app.route('/detail/p/<string:short_url>', methods=['GET','POST'])
# @login_required
# def delete2Level(short_url):
#     return detail("p/"+short_url)

# @app.route('/delete/<string:short_url>', methods=['POST', "GET"])
# @login_required
# def delete(short_url):
#     created_by = current_user.username
#     url = ShortURL.query.filter_by(shorten_url=short_url, created_by=created_by).first_or_404()
#     form_delete = DeleteForm(customize_url=url.shorten_url, the_url=url.origin_url)
#
#     if form_delete.validate_on_submit():
#         db.session.delete(url)
#         db.session.commit()
#         return redirect(url_for('index'))
#     return redirect(url_for('index'))


@app.route('/detail/<string:short_url>', methods=['GET','POST'])
@login_required
def detail(short_url):
    created_by = current_user.username
    url = ShortURL.query.filter_by(shorten_url=short_url, created_by=created_by).first_or_404()
    form = UpdateForm(customize_url=clear_public(url.shorten_url), the_url=url.origin_url, is_public=url.is_public)
    form_delete = DeleteForm(customize_url=url.shorten_url, the_url=url.origin_url)
    if form_delete.validate_on_submit():
        if form_delete.confirm.data == 'yes':
            db.session.delete(url)
            db.session.commit()
            return redirect(url_for('index'))
    elif form.validate_on_submit():
        default_shorten_url = 'Default random'
        the_url = form.the_url.data
        customize_url = clear_public(form.customize_url.data)
        is_public = form.is_public.data
        created_by = current_user.username
        while True:
            if customize_url == default_shorten_url:
                shorten_url = rehash_baseh62(the_url)  # 压缩算法或者自定义短网址，本系统的核心
                url.shorten_url = shorten_url
            # 查询这个网址有没有被压缩
            # saved_shorten_url = ShortURL.query.filter_by(origin_url)
            else:
                url.origin_url = the_url
                url.shorten_url = make_public(customize_url, is_public=='True')
                url.is_public = is_public
                url.shorten_url_created_by = customize_url+"-"+str(created_by)
            # 保存
            try:
                # 试探着保存, 如果保存成功, 那么跳出循环
                # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.add(url)
                db.session.commit()
                break
            except sa.exc.IntegrityError as e:
                print(e)
                db.session.rollback()
                saved_origin_url = db.session.query(ShortURL.origin_url).filter_by(shorten_url=customize_url, created_by=created_by).first()
                # print(shorten_url + " exists, roll back")
                # 自定义短网址命名重复
                if customize_url != default_shorten_url:
                    flash('the assgined name has been taken before')
                    return render_template('detail.html', form=form,
                                           shorten_url=make_full_url(app, customize_url),
                                           taken=True,
                                           took_url=saved_origin_url.origin_url,
                                           form_delete=form_delete)
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
        form_index = TheForm(customize_url=default_shorten_url)
        urls = ShortURL.query.filter_by(created_by=current_user.username).all()
        return render_template('index.html', form=form_index, shorten_url=make_full_url(app, customize_url, is_public), urls=urls)
    return render_template('detail.html', form=form,url=url, form_delete=form_delete)

@app.route('/<string:short_url>', methods=['GET'])
@login_required
def redirect_short_url(short_url):
    created_by = current_user.username
    url = ShortURL.query.filter_by(shorten_url=short_url, created_by=created_by).first_or_404()
    return redirect(url.origin_url)
    # origin_url = redis_client.get(short_url)
    # if not origin_url:
    #     url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    #     origin_url = url.origin_url
    #     redis_client.set(short_url, origin_url, 24*3600)
    # return redirect(origin_url)

@login_required
@app.route('/<string:short_url_prefix>/<string:short_url>', methods=['GET'])
def redirect_short_url_with_prefix(short_url, short_url_prefix):
    # origin_url = redis_client.get(short_url_prefix + '/' + short_url)
    # if not origin_url:
    created_by = current_user.username
    url = ShortURL.query.filter_by(shorten_url=short_url_prefix + '/' + short_url, created_by=created_by).first_or_404()
    origin_url = url.origin_url
    # redis_client.set(short_url_prefix + '/' + short_url, origin_url, 24*3600)
    return redirect(origin_url)


@app.route('/about')
def about():
    return render_template('about.html')







