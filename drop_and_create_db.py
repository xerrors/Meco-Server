from app import *
from app.tables import *
from app.utils.articles import scan_article_to_db

import json
import shutil

shutil.copy('data/data.db', 'data/data.db_bk')

db.drop_all()
db.create_all()
scan_article_to_db()


