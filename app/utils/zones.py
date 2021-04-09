import os
import json

from app.config import JSON_PATH

"""
_id:     ID
date:   日期     eg "2020-02-06T15:24:59.942Z"
msg:    消息内容 eg "这是内容"
status: 状态     eg "😫" （a emoji)
"""

def get_zones():
    with open(os.path.join(JSON_PATH, 'zone.json'), 'r') as f:
        data = json.load(f)
    
    return data['data']


def save_zone(data):
    with open(os.path.join(JSON_PATH, 'zone.json'), 'w') as f:
        json.dump({'data': data}, f)


def add_zone(msg:dict):
    data = get_zones()

    # 判断是否存在数据
    if len(data) == 0:
        _id = 0
    else:
        _id = data[-1]['id'] + 1
    
    msg['id'] = _id
    data.append(msg)

    save_zone(data)
    return data


def delete_zone(msg_id):
    data = get_zones()

    for i in range(len(data)):
        if data[i]['id'] == msg_id:
            del data[i]
            break

    save_zone(data)
    return data


def update_zone(msg:dict):
    data = get_zones()

    for i in range(len(data)):
        if data[i]['id'] == msg['id']:
            data[i] = msg
            break

    save_zone(data)
    return data


if __name__ == '__main__':
    JSON_PATH = '../../data'
    with open('../../../../Node/data/zoneMsg.json', 'r') as f:
        data = json.load(f)
        data = data['data']

        for i in data[::-1]:
            add_zone(i)
