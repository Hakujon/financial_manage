from datetime import datetime, timedelta


def get_start_of_week():
    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    this_week_start = this_week_start.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    return this_week_start.isoformat()


def get_end_of_week():
    this_week_end = datetime.now() + timedelta(days=(6-datetime.now().weekday()))
    this_week_end = this_week_end.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=99
    )
    return this_week_end.isoformat()


def get_start_of_month():
    this_month_start = datetime.now().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    return this_month_start.isoformat()
