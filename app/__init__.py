# coding=utf-8
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
from .plugins import comma_mode

app = Flask(__name__)

# redis_client = FlaskRedis()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

shorten_items = []
shorten_items_mapping = {}
shorten_items_init_flag = False

def init_shorten_urls(urls):
    try:
        if urls == None:
            urls = ShortURL.query.all()
        global shorten_items_init_flag
        if shorten_items_init_flag == False:
            shorten_items_init_flag = True
            for url in urls:
                shorten_items.append(url.shorten_url)
                shorten_items_mapping[url.shorten_url] = url
            print("@Log __init__.py 46 init_shorten_urls the shortened items len is ", len(shorten_items))
            print("@Log __init__.py 47 init_shorten_urls the shortened shorten_items_mapping len is ", len(shorten_items_mapping))
    except Exception as e:
        # 如果表不存在，静默失败
        print(f"Warning: Could not initialize shorten_urls: {e}")
        return

def clean_shorten_urls(url_object):
    try:
        shorten_items.remove(url_object.shorten_url)
        shorten_items_mapping.pop(url_object.shorten_url)
    except:
        pass

def add_shorten_Urls(url_object):
    try:
        if url_object.shorten_url not in shorten_items:
            shorten_items.append(url_object.shorten_url)
            shorten_items_mapping[url_object.shorten_url] = url_object
    except Exception as e:
        print("@Log Error __Init__ Line66 add_shorten_Urls ", e, type(e).__name__)

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
    with app.app_context():
        init_shorten_urls(None)
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

# ///
class TheForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()])
    customize_url = StringField("you can assgin a short name if you like, input random to generate randomly", validators=[Length(min=2, max=16)])
    is_public = RadioField('whether you want to make the shorten url public', choices=[('True', 'Yes'), ('False', 'No')], default='False')
    submit = SubmitField("shorten")

class UpdateForm(Form):
    the_url = StringField("the origin url to be shorten", validators=[DataRequired(), URL()]) # TODO 这个名字叫的不好，需要改。
    customize_url = StringField("you can assgin a short name if you like, input random to generate randomly", validators=[Length(min=2, max=16)])
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
    print("@Log __init__.py line132 make_public  public ??", is_public, shorten_url)
    return shorten_url

def clear_public(shorten_url):
    if shorten_url.startswith('p/'):
        return shorten_url[2:]
    return shorten_url

from flask import  send_file
import pandas as pd
from io import BytesIO
@app.route('/download_shortened')
def download_shortened():
    urls = ShortURL.query.filter_by(created_by=current_user.username).all()
    # 创建一个简单的DataFrame
    shortened_urls = []
    origin_urls = []
    is_public_flag = []
    for url in urls:
        shortened_urls.append(url.shorten_url)
        origin_urls.append(url.origin_url)
        is_public_flag.append(url.is_public)
    df = pd.DataFrame({
        'shortened_urls': shortened_urls,
        'origin_urls': origin_urls,
        'is_public': is_public_flag
    })
    # 使用BytesIO作为临时存储
    buffer = BytesIO()
    # 将DataFrame保存为Excel文件
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    # 重置缓冲区的位置
    buffer.seek(0)

    # 发送文件给用户
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        attachment_filename='shortended.xlsx'
    )




@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    default_shorten_url = 'random'
    form = TheForm(customize_url=default_shorten_url)
    if current_user.is_authenticated:
        urls = ShortURL.query.filter_by(created_by=current_user.username).all()
    else:
        urls = []
    if form.validate():
        the_url = form.the_url.data
        customize_url = form.customize_url.data
        is_public = form.is_public.data
        created_by = current_user.username
        while True:
            if customize_url == default_shorten_url:
                shorten_url = rehash_baseh62(the_url)  #压缩算法或者自定义短网址，本系统的核心
            else:
                shorten_url = make_public(customize_url, form.is_public.data == 'True')
            print("@Log __init__ index Line198 create url")
            url = ShortURL(origin_url=the_url, shorten_url=shorten_url,created_by=created_by, is_public=is_public, shorten_url_created_by=shorten_url+"-"+str(created_by))
            # 保存
            try:
                # 试探着保存, 如果保存成功, 那么跳出循环
                # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.add(url)
                db.session.commit() 
                print("@Log __init__ index Line206 commit")
                add_shorten_Urls(url)
                print("@Log __init__ index Line208 commit")
                break
            except sa.exc.IntegrityError as e:
                db.session.rollback()
                clean_shorten_urls(url)
                saved_origin_url = db.session.query(ShortURL.origin_url).filter_by(shorten_url=shorten_url, created_by=created_by).first()
                # print(shorten_url + " exists, roll back")
                # 自定义短网址命名重复
                if customize_url != default_shorten_url and saved_origin_url:
                    flash('the assgined name has been taken before')
                    took_url = saved_origin_url[0] # 第一个字段
                    return render_template('index.html', form=form,
                                           shorten_url=make_full_url(app, shorten_url),
                                           taken=True,
                                           took_url=took_url)
                # 没有采用自定义网址, 默认采用压缩的方式, 但是之前已经存储过 或者 压缩的时候哈希冲突
                elif customize_url == default_shorten_url:
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
                else:
                    from flask import abort
                    print("@Log __init__ index Line239 abort")
                    return abort(404, "Error Unxpected")
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


@app.route('/detail/p/<string:prefix>/<string:short_url>', methods=['GET','POST'])
@login_required
def detail2LevelWithP(prefix, short_url):
    print("Hello, I got it!")
    return extract_f1("p/" + prefix+"/"+ short_url)

@app.route('/detail/<string:prefix>/<string:short_url>', methods=['GET','POST'])
@login_required
def detail2Level(prefix, short_url):
    print("Hello, I got it!")
    return extract_f1(prefix+"/"+ short_url)

import copy

def extract_f1(short_url): # TODO 这个函数的名字实在是胡闹！
    created_by = current_user.username
    url = ShortURL.query.filter_by(shorten_url=short_url, created_by=created_by).first_or_404()
    old_url = copy.deepcopy(url)
    form = UpdateForm(customize_url=clear_public(url.shorten_url), the_url=url.origin_url, is_public=url.is_public)
    form_delete = DeleteForm(customize_url=url.shorten_url, the_url=url.origin_url)
    if form_delete.validate():
        if form_delete.confirm.data == 'yes':
            db.session.delete(url)
            db.session.commit()
            clean_shorten_urls(url)
            return redirect(url_for('index'))
    elif form.validate(): # 更新
        default_shorten_url = 'random'
        the_url = form.the_url.data # @mark
        customize_url = clear_public(form.customize_url.data)
        is_public = form.is_public.data
        created_by = current_user.username
        while True:
            if customize_url == default_shorten_url:
                shorten_url = rehash_baseh62(the_url)  # 压缩算法或者自定义短网址，本系统的核心
                url.shorten_url = shorten_url
                url.shorten_url_created_by = shorten_url + "-" + str(created_by)
            # 查询这个网址有没有被压缩
            # saved_shorten_url = ShortURL.query.filter_by(origin_url)
            else:
                url.origin_url = the_url
                url.shorten_url = make_public(customize_url, is_public == 'True')
                url.is_public = is_public
                url.shorten_url_created_by = customize_url + "-" + str(created_by)
            # 保存
            try:
                # 试探着保存, 如果保存成功, 那么跳出循环
                # shorten_url 有可能是唯一的，会引起唯一性索引异常
                db.session.add(url)
                db.session.commit()
                clean_shorten_urls(old_url)
                add_shorten_Urls(url)
                break
            except sa.exc.IntegrityError as e:
                print(e)
                db.session.rollback()
                clean_shorten_urls(url)
                add_shorten_Urls(old_url)
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
        return redirect(url_for('index'))
    return render_template('detail.html', form=form, url=url, form_delete=form_delete)


@app.route('/detail/<string:short_url>', methods=['GET','POST'])
@login_required
def detail(short_url):
    return extract_f1(short_url)

def find_similar_words(word, word_list, n=5, cutoff=0.6):
    """
    根据给定的单词，在列表中找到相似的单词。

    参数:
        word (str): 要查找的单词
        word_list (list of str): 参考单词列表
        n (int): 返回的相似单词数量，默认为5
        cutoff (float): 相似度阈值，介于0到1之间，默认为0.6

    返回:
        list of str: 相似的单词列表
    """
    import difflib
    words = difflib.get_close_matches(word, word_list, n=n, cutoff=cutoff)
    words_contains_word = [w for w in word_list if word in w]
    words.extend(words_contains_word)
    words = list(set(words))
    return words

def find_similar_urls(shorten_item):
    similar_words = find_similar_words(shorten_item, shorten_items)
    print("@Log __init__.py find_similar_urls LIne342 find_similar_urls ", similar_words)
    similar_urls = []
    for word in similar_words:
        url = shorten_items_mapping[word]  # TODO
        similar_urls.append(url)
    return similar_urls

@app.route('/p/<string:short_url>', methods=['GET'])
def redirect_public_short_url(short_url):
    short_url = "p/" + short_url
    url = ShortURL.query.filter_by(shorten_url=short_url).first()
    if url:
        return redirect(url.origin_url)
    else:
        similar_urls = find_similar_urls(short_url)
        print("@Log __init__.py L355 redirect_public_short_url similar urls is ", similar_urls)
        return render_template('404_and_similar.html', similar_urls=similar_urls)

@app.route('/<string:short_url>', methods=['GET'])
@login_required
def redirect_short_url(short_url):
    created_by = current_user.username
    final_url = ""
    if ":" in short_url:
        final_url =  comma_mode(short_url)
        return redirect(final_url)
    else:
        url = ShortURL.query.filter_by(shorten_url=short_url, created_by=created_by).first()
        if url:
            final_url = url.origin_url
            return redirect(final_url)
        else:
            similar_urls = find_similar_urls(short_url)
            print("@Log __init__.py L373 redirect_short_url similar urls is ", similar_urls)
            return render_template('404_and_similar.html', similar_urls=similar_urls)

    # origin_url = redis_client.get(short_url)
    # if not origin_url:
    #     url = ShortURL.query.filter_by(shorten_url=short_url).first_or_404()
    #     origin_url = url.origin_url
    #     redis_client.set(short_url, origin_url, 24*3600)
    # return redirect(origin_url)

@app.route('/p/<string:short_url_prefix>/<string:short_url>', methods=['GET'])
@login_required
def redirect_p_short_url_with_prefix(short_url, short_url_prefix):
    # origin_url = redis_client.get(short_url_prefix + '/' + short_url)
    # if not origin_url:
    created_by = current_user.username
    shorten_item = 'p/' + short_url_prefix + '/' + short_url
    url = ShortURL.query.filter_by(shorten_url=shorten_item, created_by=created_by).first()
    if url:
        origin_url = url.origin_url
        # redis_client.set(short_url_prefix + '/' + short_url, origin_url, 24*3600)
        return redirect(origin_url)
    else:
        similar_urls = find_similar_urls(shorten_item)
        print("@Log __init__.py L397 redirect_p_short_url_with_prefix similar urls is ", similar_urls)
        return render_template('404_and_similar.html',similar_urls=similar_urls)

@app.route('/<string:short_url_prefix>/<string:short_url>', methods=['GET'])
@login_required
def redirect_short_url_with_prefix(short_url, short_url_prefix):
    # origin_url = redis_client.get(short_url_prefix + '/' + short_url)
    # if not origin_url:
    created_by = current_user.username
    shorten_item = short_url_prefix + '/' + short_url
    url = ShortURL.query.filter_by(shorten_url=shorten_item, created_by=created_by).first()
    if url:
        origin_url = url.origin_url
        # redis_client.set(short_url_prefix + '/' + short_url, origin_url, 24*3600)
        return redirect(origin_url)
    else:
        similar_urls = find_similar_urls(shorten_item)
        print("@Log __init__.py L414 redirect_short_url_with_prefix similar urls is ", similar_urls)
        return render_template('404_and_similar.html', similar_urls=similar_urls)

@app.route('/about')
def about():
    return render_template('about.html')







