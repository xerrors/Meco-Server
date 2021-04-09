from flask import Blueprint
from flask import request, jsonify
from app import app, db
from app.utils.articles import get_articles_from_db, scan_article_to_db

mod = Blueprint('test', __name__)



# TODO 仅用作测试使用
@mod.route('/scan-article-to-db', methods=['GET'])
def scan_to_db():
    scan_article_to_db()
    articles = get_articles_from_db()
    return jsonify({"data": articles})
