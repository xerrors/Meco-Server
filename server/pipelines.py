# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from app.tables import CsdnCount, CsdnArticlesTable
from app import db

class MyBlogPipeline:

    def __init__(self):
        self.current = datetime.today().strftime('%Y-%m-%d')

    def process_item(self, item, spider):
        # 查看当前文章是否在服务器中
        if not CsdnArticlesTable.query.filter_by(article_id=item['article_id']).first():
            db.session.add(CsdnArticlesTable(
                article_id=item['article_id'],
                title=item['title'],
                create_date=item['create_date'],
            ))
            db.session.commit()

        
        csdn_count = CsdnCount.query.filter_by(
            article_id=item['article_id'],
            date=datetime.today().strftime('%Y-%m-%d')
            ).first()

        # 查看今天是否已经爬取完成
        if not csdn_count:
            db.session.add(CsdnCount(
                article_id=item['article_id'],
                read_count=item['read_count'],
                comment_count=item['comments_count'],
                date=datetime.today().strftime('%Y-%m-%d')
            ))
        else:
            csdn_count.update_count(item['read_count'], item['comments_count'])
    
        db.session.commit()

        return item
