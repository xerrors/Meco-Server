# coding=utf-8
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app, resources=r'/*')
db = SQLAlchemy(app)

from app import tables
from app.views import public, blog, admin, test

app.register_blueprint(public.mod)
app.register_blueprint(blog.mod)
app.register_blueprint(admin.mod)
app.register_blueprint(test.mod)


@app.errorhandler(404)
def page_not_found(e):
    print('123')
    return jsonify({"message": str(e)}), 404


@app.errorhandler(403)
def page_not_found(e):
    return jsonify({"message": str(e)}), 403

