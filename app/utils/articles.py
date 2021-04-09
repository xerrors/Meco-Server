import os
import frontmatter

from app import db

from app.config import BLOG_PATH
from app.tables import LocalArticlesTable, LocalArticlesComment
from app.tables import CsdnArticlesTable, CsdnCount
from app.utils.database import get_page_view_by_path


def get_article_list_from_dirs():
    assert os.path.exists(BLOG_PATH)
    article_list = []

    def extend_dir(path):
        for file in os.listdir(path):
            # 遍历所有文件
            markdown_path = os.path.join(path, file)

            # 如果是文件夹递归读取，否则读取文件
            if os.path.isdir(markdown_path):
                extend_dir(path=os.path.join(path, file))
            else:
                article_list.append(parse_markdown(markdown_path).metadata)

    extend_dir(BLOG_PATH)
    return article_list


def scan_article_to_db():
    assert os.path.exists(BLOG_PATH)
    article_list = []

    def extend_dir(path):
        for file in os.listdir(path):
            # 遍历所有文件
            markdown_path = os.path.join(path, file)

            # 如果是文件夹递归读取，否则读取文件
            if os.path.isdir(markdown_path):
                extend_dir(path=os.path.join(path, file))
            else:
                cur_frontmatter = parse_markdown(markdown_path)
                article = LocalArticlesTable.query.filter_by(path=cur_frontmatter['permalink']).first()
                if article:
                    article.local_path = markdown_path
                    db.session.commit()
                else:
                    db.session.add(LocalArticlesTable(
                        path=cur_frontmatter['permalink'],
                        local_path=markdown_path,
                    ))
                    db.session.commit()

    extend_dir(BLOG_PATH)
    return article_list


def get_articles_from_db():

    article_list = []
    query_result = LocalArticlesTable.query.all()

    for item in query_result:
        item_dict = {}
        item_dict['like_count'] = item.like_count
        item_dict['read_count'] = get_page_view_by_path(item.path)
        item_dict.update(parse_markdown(item.local_path).metadata)
        item_dict['comment_count'] = LocalArticlesComment.query.filter_by(path=item.path).count()
        article_list.append(item_dict)

    return article_list


def get_articles_from_csdn():
    """ 从数据库中找寻已经爬取的 CSDN 文章 """

    article_list = []
    query_result = CsdnArticlesTable.query.all()

    for item in query_result:
        item_dict = {}
        item_dict['title'] = item.title
        item_dict['date'] = item.create_date
        item_dict['article_id'] = item.article_id

        article_count = CsdnCount.query.filter_by(article_id=item.article_id).first()

        item_dict['read_count'] = article_count.read_count
        item_dict['comment_count'] = article_count.comment_count

        article_list.append(item_dict)

    return article_list


def get_articles_from_zhihu():
    return []


def parse_markdown(markdown_path):
    with open(markdown_path, encoding='UTF-8') as f:
        md = frontmatter.load(f)
        # 去除不规范的链接名称
        if md['permalink'][0] == '/':
            md['permalink'] = md['permalink'][1:]
        return md


def rename_markdown(md):
    # 解析文件名并根据分类保存到对应的文件目录下
    path = md['permalink'][1:] if md['permalink'][0] == '/' else md['permalink']

    file_name = md['date'].strftime('%Y-%m-%d') + '-' + md['title'].replace(' ', '-') + '.md'

    if type(md.get('categories')) == type([]):
        file_path = os.path.join(BLOG_PATH, md.get('categories')[0])
    elif type(md.get('categories')) == type(""):
        file_path = os.path.join(BLOG_PATH, md.get('categories'))
    else:
        file_path = os.path.join(BLOG_PATH, 'Others')

    if md.get('zhuanlan'):
        file_path = os.path.join(file_path, md.get('zhuanlan'), file_name)
    else:
        file_path = os.path.join(file_path, file_name)

    # 判断该文章是否是已经存在数据库或者本地路径里面
    item = LocalArticlesTable.query.filter_by(path=path).first()

    if item and os.path.exists(item.local_path):
        os.remove(item.local_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    os.renames('temp.md', file_path)
    return file_path


# def rebuild():
#     def extend_dir(path):
#         for file in os.listdir(path):
#             # 遍历所有文件
#             markdown_path = os.path.join(path, file)

#             # 如果是文件夹递归读取，否则读取文件
#             if os.path.isdir(markdown_path):
#                 extend_dir(path=os.path.join(path, file))
#             else:
#                 md = parse_markdown(markdown_path)

#                 file_name = md['date'].strftime('%Y-%m-%d') + '-' + md['title'].replace(' ', '-') + '.md'
#                 if type(md.get('categories')) == type([]):
#                     file_path = os.path.join(BLOG_PATH, md.get('categories')[0])
#                 elif type(md.get('categories')) == type(""):
#                     file_path = os.path.join(BLOG_PATH, md.get('categories'))
#                 else:
#                     file_path = os.path.join(BLOG_PATH, 'Others')

#                 if md.get('zhuanlan'):
#                     file_path = os.path.join(file_path, md.get('zhuanlan'), file_name)
#                 else:
#                     file_path = os.path.join(file_path, file_name)
                
#                 os.renames(markdown_path, file_path)

#     extend_dir(BLOG_PATH)

