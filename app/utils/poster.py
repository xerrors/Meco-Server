import os
import json

from app.config import JSON_PATH

"""
cover:
link:
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

    # 如果已存在就直接更新
    for i in range(len(data)):
        if data[i]['link'] == post['link']:
            data[i] = post
            return "已存在，更新成功"

    # 否在在原数据上面追加
    data.append(post)

    save_poster(data)
    return "添加成功"


def delete_poster(link):
    data = get_posters()

    for i in range(len(data)):
        if data[i]['link'] == link:
            del data[i]
            break

    save_poster(data)
    return data
