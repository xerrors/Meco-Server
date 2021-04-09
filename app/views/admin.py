from flask import Blueprint
from flask import request, jsonify, abort, json, session
from app import app, db
from app.utils.articles import get_article_list_from_dirs, get_articles_from_db, scan_article_to_db, rename_markdown
from app.utils.articles import get_articles_from_zhihu, get_articles_from_csdn
from app.utils.validate import validate_server_token
from app.utils.database import get_all_messages
from app.tables import LocalArticlesTable, Messages

import frontmatter

mod = Blueprint('admin', __name__, url_prefix='/admin')


def not_login(msg='登录之后再试~'):
    return jsonify({"message": '登录之后再试~', 'code': 2000})


# 获取文章列表
@mod.route('/articles', methods=["GET"])
def get_articles():
    print(session.get('login'))
    if not session.get('login'):
        return not_login()

    source = request.args.get('source')
    if source == 'csdn':
        articles = get_articles_from_csdn()
    elif source == 'zhihu':
        articles = get_articles_from_zhihu()
    elif source == 'db':
        articles = get_articles_from_db()
    elif source == 'local':
        articles = get_article_list_from_dirs()
    else:
        return jsonify({"message": "没有该来源的文章~"}), 404
    return jsonify({"data": articles})


@mod.route('/articles/md_source', methods=["GET"])
def get_markdown():
    if not session.get('login'):
        return not_login()

    path = request.args.get('path')

    item = db.session.query(LocalArticlesTable).filter_by(path=path).first()

    if not item:
        scan_article_to_db()
        item = db.session.query(LocalArticlesTable).filter_by(path=path).first()

    if item:
        with open(item.local_path, encoding='UTF-8') as f:
            data = f.read()
            return jsonify({"data": data})
    else:
        abort(404, "不存在该文章！")


@mod.route('/articles/md_source', methods=["POST"])
def upload_markdown():
    if not session.get('login'):
        return not_login()

    # 修改逻辑：对于已经存在的文章，应该发来该文章的 path，通过比对两次的 local 的 path
    # 是否相同，然后决定是否对目录下的文章进行扫描

    md = request.get_data()
    with open('temp.md', 'wb+') as f:
        f.write(md)
    with open('temp.md', encoding='UTF-8') as f:
        md = frontmatter.load(f)

    if not md.get('title') or not md.get('date') or not md.get('permalink'):
        abort(404, '请上传符合博客文章要求的文章~')

    file_path = rename_markdown(md)
    path = request.args.get('path')
    item = db.session.query(LocalArticlesTable).filter_by(path=path).first()

    if not item or file_path != item.local_path:
        scan_article_to_db()

    # TODO: 后续需要添加自动编译提交的功能，但考虑到 vuepress 编译太慢了
    return jsonify({"message": "已经保存到{}".format(file_path)})


@mod.route('/login', methods=["POST"])
def admin_login():
    if session.get('login'):
        return jsonify({"message": '你已经登录过了~', "code": '1000'})

    data = request.get_data()
    data = json.loads(data)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": '把所有空都填上~别落下~', "code": '1001'})

    if validate_server_token(username, password):
        from datetime import timedelta
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)  # 存活60分钟
        session['login'] = 'True'
        print(session.get('login'))
        return jsonify({"message": '登录成功~', "code": '1000'})
    else:
        return jsonify({"message": '你不对劲！', "code": '1001'})


@mod.route('/messages', methods=["GET"])
def get_messages():
    if not session.get('login'):
        return not_login()

    source = request.args.get('source')
    if source == 'db':
        msgs = get_all_messages()
    else:
        msgs = []
    return jsonify({"data": msgs})


@mod.route('/readmessage', methods=["POST"])
def read_message():
    if not session.get('login'):
        return not_login()

    id = request.args.get('id')
    if not id:
        abort(404, "请提供id~")
    if id == 'all':
        msgs = db.session.query(Messages).all()
        for msg in msgs:
            msg.set_as_readed()
        db.session.commit()
    else:
        msg = db.session.query(Messages).get(id)
        if msg:
            msg.set_as_readed()
            db.session.commit()
        else:
            abort(403, "不存在该id")

    msgs = get_all_messages()
    return jsonify({"message": "Success", "data": msgs})


@mod.route('/logout', methods=["POST"])
def admin_logout():
    if session.get('login'):
        session.pop('login')
        return jsonify({"message": '退出成功~', "code": '1000'})
    else:
        return not_login()
