from flask import Blueprint
from flask import request, jsonify, abort, json, session
from app import app, db
from app.utils.articles import get_article_list_from_dirs, get_articles_from_db, scan_article_to_db, save_md_to_file
from app.utils.articles import get_articles_from_juejin, get_articles_from_csdn, parse_markdown
from app.utils.validate import validate_server_token
from app.utils.database import get_all_messages
from app.utils.poster import get_posters, add_poster, delete_poster, set_as_top
from app.utils.count import get_all_count, get_last_days
from app.utils.private import ALI_ACCESSKEY_ID, ALI_ACCESSKEY_SECRET, ALI_BUCKET, ALI_ENDPOINT
from app.tables import LocalArticlesTable, Messages
from app.config import PREFIX, DATA_PATH

from monitor.status import MachineStatus

from datetime import datetime

import os
import frontmatter

mod = Blueprint('admin', __name__, url_prefix=PREFIX + '/admin')

deploy_status = 0
ms = MachineStatus()


def not_login(msg='登录之后再试~'):
    return jsonify({"message": '登录之后再试~', 'code': 2000})


# 获取文章列表
@mod.route('/articles', methods=["GET"])
def get_articles():
    if not session.get('login'):
        return not_login()

    source = request.args.get('source')
    if source == 'csdn':
        articles = get_articles_from_csdn()
    elif source == 'juejin':
        articles = get_articles_from_juejin()
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

    if path == 'draft':
        draft_path = os.path.join(DATA_PATH, 'draft.md')
        if os.path.exists(draft_path):
            with open(draft_path, encoding='UTF-8') as f:
                data = f.read()
                return jsonify({"data": data})
        else:
            return jsonify({"data": ""})

    item = db.session.query(LocalArticlesTable).filter_by(path=path).first()

    if not item:
        scan_article_to_db()
        item = db.session.query(
            LocalArticlesTable).filter_by(path=path).first()

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

    md = request.get_data()
    path = request.args.get('path')
    revision = request.args.get('revision')

    fm = parse_markdown(md, True)
    if not fm.get('title') or not fm.get('date') or not fm.get('permalink'):
        return jsonify({"message": "信息有误", "code": "403"})

    # 如果是草稿文件是临时保存在草稿文件 draft.md 里面的
    if path == "draft":
        draft_path = os.path.join(DATA_PATH, 'draft.md')
        with open(draft_path, 'wb+') as f:
            f.write(md)

        # 判断是否作为正式文章保存
        if revision != "1":
            return jsonify({"message": "已经保存为草稿"})
        else:
            if fm.get('permalink') == 'draft':
                return jsonify({"message": "permalink 不能是 draft", "code": "403"})

            file_path = save_md_to_file(md, cur_path=draft_path)
            return jsonify({"message": "新建文章{}".format(file_path), "data": fm.get('permalink')})

    else:  
        if revision:      
            if fm.get('permalink') != path:
                return jsonify({"message": "不能修改 permalink，请重新修改~", "code": "403"})
            else:
                # 添加版本控制
                pass
        
        file_path = save_md_to_file(md)
        return jsonify({"message": "已经保存到{}".format(file_path)})


@mod.route('/logged', methods=["GET"])
def check_is_logged():
    if session.get('login'):
        from datetime import timedelta
        app.permanent_session_lifetime = timedelta(minutes=60)  # 更新存活时间
        return jsonify({"code": '1000', "message": "已登录"})
    else:
        return jsonify({"code": '2000', "message": "未登录"})


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


@mod.route('/hide-comment', methods=["GET"])
def hide_comment():
    # TODO: 完善
    pass


@mod.route('/post-image', methods=["POST"])
def route_post_image():
    # 鉴权
    if not session.get('login'):
        return not_login()
    import oss2

    # 获取图片文件以及参数设置
    image_file = request.get_data()
    filename = request.args.get('filename')
    rename_format = request.args.get('rename_format')

    if not filename:
        return jsonify({"message": "这不是我干出来的事情"})

    if not rename_format:
        name = 'imgs/' + filename
    else:
        name = 'imgs/{}-{}'.format(datetime.now().strftime(rename_format),
                                   filename.replace(' ', '-'))

    # 创建实例并上传文件
    bucket = oss2.Bucket(
        oss2.Auth(ALI_ACCESSKEY_ID, ALI_ACCESSKEY_SECRET),
        ALI_ENDPOINT,
        ALI_BUCKET)

    bucket.put_object(name, image_file)

    return jsonify({
        "message": "Success",
        "data": "https://{}.{}/{}".format(ALI_BUCKET, ALI_ENDPOINT, name)})


@mod.route('/poster', methods=["GET"])
def route_get_posters():
    return jsonify({"message": "Success", "data": get_posters()})


@mod.route('/poster', methods=["POST"])
def route_add_poster():
    if not session.get('login'):
        return not_login()

    data = request.get_data()
    data = json.loads(data)
    _cover = data.get("cover")
    _link = data.get("link")

    if not _cover or not _link:
        return abort(403, "信息不足")

    msg = add_poster({
        'cover': _cover,
        'link': _link,
        'text': data.get('text'),
        'type': data.get('type') or "local",
        'top': bool(data.get('top')),
    })

    return jsonify({"message": msg, "data": get_posters()})


@mod.route('/poster', methods=["DELETE"])
def route_delete_poster():
    if not session.get('login'):
        return not_login()

    _id = request.args.get('id')
    if not _id:
        return jsonify({"message": "信息不足", "data": get_posters()})

    return jsonify({"message": "已受理", "data": delete_poster(_id)})


@mod.route('/poster/settop', methods=["GET"])
def route_set_as_top():
    if not session.get('login'):
        return not_login()

    _id = request.args.get('id')
    if not _id:
        return jsonify({"message": "信息不足", "data": get_posters()})
    else:
        set_as_top(_id)

    return jsonify({"message": "已受理", "data": get_posters()})


# 获取主站数据
@mod.route('/count/all', methods=["GET"])
def route_count_all():
    if not session.get('login'):
        return not_login()

    return jsonify({"data": get_all_count()})


# 获取主站数据
@mod.route('/count/days', methods=["GET"])
def route_count_days():
    if not session.get('login'):
        return not_login()

    days = request.args.get('days')

    return jsonify({"data": get_last_days(int(days) or 90)})


# 获取服务器状态信息
@mod.route('/status', methods=["GET"])
def route_server_status():
    if not session.get('login'):
        return not_login()

    ms.get_status_info()
    status = {
        'status': ms.status,
        'cpu': ms.cpu,
        'mem': ms.mem,
        'network': ms.network,
        'process': ms.process
    }
    return jsonify({"data": status})


@mod.route('/logout', methods=["POST"])
def admin_logout():
    if session.get('login'):
        session.pop('login')
        return jsonify({"message": '退出成功~', "code": '1000'})
    else:
        return not_login()


@mod.route('/deploy-vuepress', methods=["GET"])
def deploy_vuepress():
    global deploy_status
    if deploy_status == 'waiting':
        return jsonify({"message": '等待中~'})
    else:
        deploy_status = 'waiting'
        deploy_status = os.system("bash ~/Meco/deploy.sh")
        if deploy_status == 0:
            return jsonify({"message": '编译完成~'})
        else:
            return jsonify({"message": '或许在编译的时候出现了什么问题~'})
