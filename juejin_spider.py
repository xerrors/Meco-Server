# 掘金使用的是前后端分离技术开发的，可以简单的使用 API　来获取文章列表
import requests
import json

from datetime import datetime, date

from app import db
from app.tables import JuejinArticlesTable, JuejinCount

JUEJIN_ID = "4248168660734280"

# 首页地址
url = "https://api.juejin.cn/content_api/v1/article/query_list"

# 伪装成浏览器
headers = {
    'X-Legacy-Device-Id': '1574318487465',
    'Origin': 'https://juejin.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    'X-Legacy-Token': 'eyJhY2Nlc3NfdG9rZW4iOiJBNVNuRUNPb1Jad0doWm1wIiwicmVmcmVzaF90b2tlbiI6IkpuVkFoZFozdjNFdDZMOFMiLCJ0b2tlbl90eXBlIjoibWFjIiwiZXhwaXJlX2luIjoyNTkyMDAwfQ==',
    'Content-Type': 'application/json',
    'Referer': 'https://juejin.cn',
    'X-Legacy-Uid': '5dd631975188254e310b4cbb',
}


payload = {
    'cursor': '0',
    'user_id': JUEJIN_ID,
    'sort_type': 2
}

article_list = []

while payload["cursor"] == "0" or int(result["cursor"]) < int(result["count"]):
    result = requests.post(url=url, headers=headers, data=json.dumps(payload)).content.decode('utf-8')
    result = json.loads(result)
    if not result['data']:
        print("no result")
        break
    payload['cursor'] = result["cursor"]
    for i in result['data']:
        article_list.append({
            "article_id": i["article_info"]["article_id"],
            "draft_id": i["article_info"]["draft_id"],
            "title": i["article_info"]["title"],
            "content": i["article_info"]["brief_content"],
            "create_date": datetime.fromtimestamp(int(i["article_info"]["ctime"])),
            "read_count": i["article_info"]["view_count"],
            "comments_count": i["article_info"]["comment_count"],
            "like_count": i["article_info"]["digg_count"]
        })


# 保存到数据库
for item in article_list:
    if not JuejinArticlesTable.query.filter_by(article_id=item['article_id']).first():
        db.session.add(JuejinArticlesTable(
            article_id=item['article_id'],
            draft_id=item['draft_id'],
            title=item['title'],
            create_date=item['create_date'].strftime('%Y-%m-%d %H:%M:%S'),
        ))
        db.session.commit()

    
    juejin_count = JuejinCount.query.filter_by(
        article_id=item['article_id'],
        date=datetime.today().strftime('%Y-%m-%d')
        ).first()

    # 查看今天是否已经爬取完成
    if not juejin_count:
        db.session.add(JuejinCount(
            article_id=item['article_id'],
            read_count=item['read_count'],
            comment_count=item['comments_count'],
            like_count=item['like_count'],
            date=datetime.today().strftime('%Y-%m-%d')
        ))
    else:
        juejin_count.update_count(item['read_count'], item['comments_count'], item['like_count'])

    db.session.commit()