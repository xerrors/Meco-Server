import os
import json

from app.config import JSON_PATH
from app.utils.mass import string_to_md5

"""
cover:
link:
text:
type:
top:
"""

def get_posters():
    with open(os.path.join(JSON_PATH, 'poster.json'), 'r') as f:
        data = json.load(f)
    
    return data['data']


def save_poster(data):
    with open(os.path.join(JSON_PATH, 'poster.json'), 'w') as f:
        json.dump({'data': data}, f)


def add_poster(post:dict):
    data = get_posters()

    post['id'] = string_to_md5(post['link'])

    if post['top']:
        for i in data:
            i['top'] = False

    # 否在在原数据上面追加
    data.append(post)

    save_poster(data)
    return "添加成功"


def set_as_top(_id):
    data = get_posters()

    for i in data:
        if i['id'] == _id:
            i['top'] = True
        else:
            i['top'] = False

    save_poster(data)


def delete_poster(_id):
    data = get_posters()

    if len(data) == 1:
        return data

    for i in range(len(data)):
        if data[i]['id'] == _id:
            del data[i]
            break

    save_poster(data)
    return data
