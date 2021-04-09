from flask import Blueprint
from flask import request, jsonify, abort
from app import app, db
from app.utils.articles import parse_markdown, get_articles_from_db
from app.utils.database import rtn_zones, get_all_zhuanlan, get_page_view_by_path, rtn_friends
from app.config import DOMAIN_PRE, TOKEN
from app.tables import Zone, FriendsTable, ZhuanlanTable, LocalArticlesTable, LocalArticlesComment, Messages
from datetime import datetime

from app.utils.zones import get_zones, delete_zone, update_zone, add_zone

mod = Blueprint('blog', __name__)


@mod.route("/visit", methods=["GET"])
def visit():
    path = request.args.get('path')

    if not path:
        abort(403, "有毛病吧！")

    from app.tables import PageViewTable
    db.session.add(PageViewTable(
        ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
        path=path,
        user_agent=request.user_agent.browser,
    ))
    db.session.commit()

    count = get_page_view_by_path(request.args.get("count"))
    return jsonify({"message": "Welcome", "data": count})


# 动态相关

@mod.route('/zones', methods=['GET'])
def get_zones_view():
    return jsonify({"data": get_zones()})


@mod.route('/zones', methods=['DELETE'])
def del_zone():
    _id = request.args.get('id')
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")
    elif _id:
        delete_zone(_id)
        return jsonify({"message": "已删除", "data": get_zones()})
    else:
        return jsonify({"message": "请提供删除的动态的 id"}), 403


@mod.route('/zones', methods=["POST"])
def create_zone():
    msg = request.args.get('msg')
    status = request.args.get('status')
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")
    add_zone({
        'msg': msg,
        'status': status,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return jsonify({"data": get_zones()})


# 友链信息


@mod.route('/friends', methods=["GET"])
def get_friends():
    id = request.args.get('id')
    if id:
        friend = db.session.query(FriendsTable).get(id)
        if friend:
            return jsonify({"message": "ok", "data": friend.to_json()})
        else:
            return jsonify({"message": "没有该动态~"}), 404
    return jsonify({"data": rtn_friends()})


@mod.route('/friends', methods=["POST"])
def add_friend():
    name = request.args.get("name")
    avatar = request.args.get("avatar")
    title = request.args.get("title")
    mail = request.args.get("mail")
    site = request.args.get("site")
    quote = request.args.get("quote")
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")

    if not name or not site or not quote:
        abort(403, "信息不全~")

    db.session.add(FriendsTable(name=name, avatar=avatar, title=title, mail=mail, site=site, quote=quote))
    db.session.commit()
    return jsonify({"data": rtn_friends()})


@mod.route('/friends', methods=['DELETE'])
def del_friend():
    id = request.args.get('id')
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")
    elif id:
        friend = db.session.query(FriendsTable).get(id)
        if friend:
            db.session.delete(friend)
            db.session.commit()
            return jsonify({"message": "已删除", "data": rtn_friends()})
        else:
            return abort(403, "删除错误~")
    else:
        return abort(403, "请提供id")


# 专栏信息


@mod.route('/zhuanlan', methods=["GET"])
def get_zhuanlan():
    if request.args.get("name"):
        result = db.session.query(ZhuanlanTable).filter_by(name=request.args.get("name")).first()
        return jsonify({"message": "here", "data": result.to_json()})
    else:
        return jsonify({"message": "here", "data": get_all_zhuanlan()})


@mod.route('/zhuanlan', methods=["POST"])
def add_zhuanlan():
    name = request.args.get("name")
    title = request.args.get("title")
    cover = request.args.get("cover")
    details = request.args.get("details")
    description = request.args.get("description")
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")
    elif not name or not title or not description:
        abort(403, "你就不对劲！")
    else:
        db.session.add(ZhuanlanTable(
            name=name,
            title=title,
            cover=cover,
            details=details,
            description=description
        ))
        db.session.commit()
        return jsonify({"message": "success", "data": get_all_zhuanlan()})


@mod.route('/zhuanlan', methods=['DELETE'])
def del_zhuanlan():
    id = request.args.get('id')
    token = request.args.get('token')

    if token != TOKEN:
        abort(403, "Token 不对劲！")
    elif id:
        zhuanlan = db.session.query(ZhuanlanTable).get(id)
        if zhuanlan:
            db.session.delete(zhuanlan)
            db.session.commit()
            return jsonify({"message": "success", "data": get_all_zhuanlan()})
        else:
            return abort(403, "删除错误~")
    else:
        return abort(403, "请提供id")


# 获取文章列表
@mod.route('/articles', methods=["GET"])
def get_articles():
    articles = get_articles_from_db()
    return jsonify({"data": articles})


# 点赞评论

# TODO 数据验证，多次点击验证 IP
# 文章点赞功能
@mod.route('/articles/like', methods=['POST'])
def add_like():
    path = request.args.get('path')
    item = db.session.query(LocalArticlesTable).filter_by(path=path).first()
    if not item:
        abort(403, "你不对劲！")

    item.add_like()
    md = parse_markdown(item.local_path).metadata
    db.session.add(Messages(
        type="like",
        date=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        link=DOMAIN_PRE + path,
        content="有人点赞了你的文章《{}》".format(md['title'])
    ))
    db.session.commit()
    return jsonify({"message": "感谢支持~"})


# TODO 数据验证
# 文章评论功能
@mod.route('/articles/comment', methods=['POST'])
def add_comment():
    path = request.args.get('path')
    reviewer = request.args.get('reviewer')
    reviewer_mail = request.args.get('reviewer_mail')
    content = request.get_data()
    content = str(content, encoding="utf-8")
    follow_id = request.args.get('follow_id')
    follow_name = request.args.get('follow_name')
    item = db.session.query(LocalArticlesTable).filter_by(path=path).first()

    if not item:
        abort(403, "你不对劲！")

    if len(content) == 0:
        return abort(403, "你不对劲~")

    # 生成评论的消息
    md = parse_markdown(item.local_path).metadata
    if reviewer:
        comment_msg = "网友“{}”评论了你的文章《{}》".format(reviewer, md['title'])
    else:
        comment_msg = "有人评论了你的文章《{}》".format(md['title'])

    db.session.add(LocalArticlesComment(
        path=path,
        reviewer=reviewer,
        reviewer_mail=reviewer_mail,
        content=content,
        follow_id=follow_id,
        follow_name=follow_name,
        date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ))
    db.session.add(Messages(
        type="comment",
        link=DOMAIN_PRE + path,
        content=comment_msg,
        date=datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ))
    db.session.commit()
    return jsonify({"message": "Good"})


@mod.route('/articles/comment', methods=['GET'])
def get_comments():
    path = request.args.get('path')
    if not path:
        abort(403, "你就是不对劲，搞事情啊~")
    query_result = db.session.query(LocalArticlesComment).filter_by(path=path).all()
    comments = [result.to_json() for result in query_result]
    return jsonify({"message": "Good!", "data": comments})

