from app.tables import Messages, LocalArticlesComment, PageViewTable

from datetime import datetime, date
from datetime import timedelta

time_format = "%Y-%m-%d %H:%M:%S"
date_format = "%Y-%m-%d"


def get_days_ago(days, have_time=False):
    return date.today() - timedelta(days=days)


def get_timezone_messages(start, end=date.today()):
    return Messages.query.filter(
        Messages.date <= end
    ).filter(
        Messages.date > start
    )


def get_timezone_pv(start, end=date.today()):
    return PageViewTable.query.filter(
        PageViewTable.date <= end
    ).filter(
        PageViewTable.date > start
    )

def get_all_count():
    # TODO：如果访问量大的话，首先是第一次访问的时候计算并保存起来，之后访问的时候直接取出来就行了
    day_ago = get_days_ago(1)
    week_ago = get_days_ago(7)
    month_ago = get_days_ago(30)

    month_message = get_timezone_messages(month_ago)
    week_message = month_message.filter(Messages.date > week_ago)
    day_message = week_message.filter(Messages.date > day_ago)

    month_pv = get_timezone_pv(month_ago)
    week_pv = month_pv.filter(PageViewTable.date > week_ago)
    day_pv = week_pv.filter(PageViewTable.date > day_ago)

    day_pv_count = day_pv.count()
    week_pv_count = week_pv.count()
    month_pv_count = month_pv.count()
    

    day_like_count = day_message.filter(Messages.type=='like').count()
    week_like_count = week_message.filter(Messages.type=='like').count()
    month_like_count = month_message.filter(Messages.type=='like').count()
    
    day_comment_count = day_message.count() - day_like_count
    week_comment_count = week_message.count() - week_like_count
    month_comment_count = month_message.count() - month_like_count

    all_pv = PageViewTable.query.count()
    all_comment = LocalArticlesComment.query.count()
    all_like = Messages.query.count() - all_comment

    data_count = {
        "pv": {
            "all": PageViewTable.query.count(),
            "day": day_pv_count,
            "week": week_pv_count,
            "month": month_pv_count
        },
        "like": {
            "all": all_like,
            "day": day_like_count,
            "week": week_like_count,
            "month": month_like_count
        },
        "comment": {
            "all": all_comment,
            "day": day_comment_count,
            "week": week_comment_count,
            "month": month_comment_count
        }
    }

    return data_count

