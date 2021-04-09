from app import *
from app.tables import *
from app.utils.articles import scan_article_to_db
from app.config import DATABASE

import json
import shutil

shutil.copy(DATABASE, DATABASE+'_bk')

db.drop_all()
db.create_all()
scan_article_to_db()


