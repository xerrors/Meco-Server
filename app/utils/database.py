from app import db
from app.tables import Zone, Messages, PageViewTable, FriendsTable, ZhuanlanTable

def rtn_zones():
    query_result = Zone.query.all()
    zones = [zone.to_json() for zone in query_result]
    return zones


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


def get_page_view_by_path(path):
    count = 0
    if not path:
        count = db.session.query(PageViewTable).count()
    else:
        count = db.session.query(PageViewTable).filter_by(path=path).count()
    
    return count