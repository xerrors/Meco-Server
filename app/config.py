import os
import sys
from app import app

Debug=True

CSDN_NAME="jaykm"
JUEJIN_ID = "4248168660734280"
BLOG_PATH = '../Meco/docs/blog/'
DATA_PATH = 'data'
DATABASE = '../data/data.db'

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = prefix + os.path.join(app.root_path, DATABASE)

DOMAIN_PRE = "https://www.xerrors.fun/"

PREFIX = '/api'

SECRET_KEY = "&%J87jVyt68JbF68IbvTG79kBy*"