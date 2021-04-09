from app import db
from datetime import datetime


class Zone(db.Model):
    __tablename__ = 'ZoneTable'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    date = db.Column(db.String(20))
    msg = db.Column(db.Text)
    status = db.Column(db.String(20))

    def to_json(self):
        json_zone = {
            'id': self.id,
            'date': self.date,
            'msg': self.msg,
            'status': self.status
        }
        return json_zone


class CsdnArticlesTable(db.Model):
    __tablename__ = 'CsdnArticlesTable'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.String(20))
    title = db.Column(db.String(60))
    create_date = db.Column(db.String(30))


class CsdnCount(db.Model):
    __tablename__ = 'CsdnReadCount'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.String(20), db.ForeignKey('CsdnArticlesTable.article_id'))
    date = db.Column(db.String(30))
    read_count = db.Column(db.Integer)
    comment_count = db.Column(db.Integer)

    def update_count(self, read, comment):
        self.read_count = read
        self.comment_count = comment


class LocalArticlesTable(db.Model):
    __tablename__ = 'LocalArticlesTable'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(50), unique=True)
    local_path = db.Column(db.String(50))
    read_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)

    def add_like(self):
        self.like_count += 1

    def add_read(self):
        self.read_count += 1


class LocalArticlesComment(db.Model):
    __tablename__ = 'LocalArticlesComment'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(50), db.ForeignKey('LocalArticlesTable.path'))
    date = db.Column(db.String(30))
    reviewer = db.Column(db.String(20))
    reviewer_mail = db.Column(db.String(30))
    follow_id = db.Column(db.Integer, default=None) # 被评论的评论的 id
    follow_name = db.Column(db.String(20), default=None) # 被评论的评论的 name
    content = db.Column(db.Text)

    def to_json(self):
        json_comment = {
            'id': self.id,
            'path': self.path,
            'date': self.date,
            'reviewer': self.reviewer,
            'reviewer_mail': self.reviewer_mail,
            'follow_id': self.follow_id,
            'follow_name': self.follow_name,
            'content': self.content,  
        }
        return json_comment


class Messages(db.Model):
    __tablename__ = 'Messages'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(30))
    type = db.Column(db.String(20))
    link = db.Column(db.String(50))
    content = db.Column(db.Text)
    readed = db.Column(db.Boolean, default=False)

    def set_as_readed(self):
        self.readed = True

    def to_json(self):
        json_msgs = {
            'id': self.id,
            'date': self.date,
            'type': self.type,
            'link': self.link,
            'content': self.content,
            'readed': self.readed,
        }
        return json_msgs


class FriendsTable(db.Model):
    __tablename__ = "FriendsTable"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    avatar = db.Column(db.String(50))
    title = db.Column(db.String(20))
    mail = db.Column(db.String(20))
    site = db.Column(db.String(20))
    quote = db.Column(db.String(50))

    def to_json(self):
        json_friends = {
            'id':  self.id,
            'name':  self.name,
            'avatar':  self.avatar,
            'title': self.title,
            'mail': self.mail,
            'site': self.site,
            'quote': self.quote,
        }
        return json_friends


class PageViewTable(db.Model):
    __tablename__ = "PageViewTable"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(30))
    domain = db.Column(db.String(30), default="")
    date = db.Column(db.DateTime, default=datetime.utcnow)
    path = db.Column(db.String(50)) # 去除协议和域名的路径部分
    user_agent = db.Column(db.String(20))


class ZhuanlanTable(db.Model):
    __tablename__ = "ZhuanlanTable"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(10))
    title = db.Column(db.String(30))
    cover = db.Column(db.String(50))
    description = db.Column(db.String(100))
    details = db.Column(db.Text)

    def to_json(self):
        json_data = {
            "id": self.id,
            "name": self.name,
            "date": self.date,
            "title": self.title,
            "cover": self.cover,
            "description": self.description,
            "details": self.details,
        }
        return json_data


# 暂时觉得没有启用的必要
# class Visitors(db.Model):
#     __tablename__ = "Visitors"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     avatar = db.Column(db.String(50))  # 头像的链接，暂时不启用
#     email = db.Column(db.String(20))
#     site = db.Column(db.String(20))
