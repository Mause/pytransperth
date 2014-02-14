import datetime


def format_date(date=None):
    """
    Takes a datetime.date object (or defaults to today)
    and returns it formatted just the way the transperth
    api likes 'em
    """
    date = date or datetime.date.today()

    return date.strftime('%A, %d %B %Y')


def clean(iterator):
    """
    Takes an iterator of strings and removes those that consist
    that str.strip considers to consist entirely of whitespace
    """
    iterator = map(str.strip, iterator)
    return list(filter(bool, iterator))
