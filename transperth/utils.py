import datetime


def format_date(date=None):
    """
    Takes a datetime.date object (or defaults to today)
    """
    date = date or datetime.date.today()

    return date.strftime('%A, %d %B %Y')


def clean(iterator):
    iterator = map(str.strip, iterator)
    return list(filter(bool, iterator))
