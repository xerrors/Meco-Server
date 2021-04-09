import os
import sys
from app import app

BLOG_PATH = '../blog/blog'
Debug=True
CSDN_NAME="jaykm"

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

DATABASE = '../data/data.db'

JSON_PATH = 'data'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = prefix + os.path.join(app.root_path, DATABASE)

SECRET_KEY = "&%J87jVyt68JbF68IbvTG79kBy*"

ADMIN_NAME = "1"
SERVER_TOKEN = "1"

DOMAIN_PRE = "https://www.xerrors.fun/"

TOKEN = "szmmzmf"