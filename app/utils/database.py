from sqlalchemy.sql.expression import desc
from app import db
from app.tables import Messages, PageViewTable, FriendsTable, ZhuanlanTable

def rtn_friends():
    query_result = db.session.query(FriendsTable).all()
    friends = [friend.to_json() for friend in query_result]
    return friends


def get_all_messages():
    query_result = Messages.query.all()
    msgs = [msg.to_json() for msg in query_result]
    return msgs


def get_all_zhuanlan():
    result = db.session.query(ZhuanlanTable).all()
    zhuanlans = [item.to_json() for item in result]
    return zhuanlans


def get_page_view_count_by_path(path):
    count = 0
    if not path:
        count = db.session.query(PageViewTable).filter(PageViewTable.user_agent!='google').count()
    else:
        count = db.session.query(PageViewTable).filter(PageViewTable.user_agent!='google').filter_by(path=path).count()
    
    return count


def get_page_view_by_path(path, limit=100):
    if not path:
        return db.session.query(PageViewTable).filter(PageViewTable.user_agent!='google').limit(limit).all()
    else:
        return db.session.query(PageViewTable).filter(PageViewTable.user_agent!='google').filter_by(path=path).limit(limit).all()


def get_all_page_view_log(cursor=0):
    assert type(cursor) == int and cursor >= 0
    query_result = PageViewTable.query.filter(PageViewTable.user_agent != 'google')
    query_result = query_result.order_by(desc(PageViewTable.id)).limit(100).offset(100*int(cursor)).all()
    items = [item.to_json() for item in query_result]
    return items
    