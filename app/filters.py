import datetime
from flask import session
from app import app, now
import pytz


@app.template_filter()
def localize(dt) -> datetime.datetime:

    if 'timezone' not in session:
        return dt
    dt = pytz.utc.localize(dt)
    tz = pytz.timezone(session['timezone'])
    local = dt.astimezone(tz)
    return local


@app.template_filter()
def dt_from_now(dt) -> str:
    """Compares datetime to now, returning a string formatted as '(in) x years/days/hours/minutes/seconds (ago)'"""
    n = now()
    past = n > dt
    delta = n - dt if past else dt - n
    if delta.days > 550:
        string = str(round(delta.days / 365)) + " years"
    elif delta.days > 185:
        string = " a year"
    elif delta.total_seconds() > 130000:
        string = str(round(delta.total_seconds() / 86400)) + " days"
    elif delta.total_seconds() > 86000:
        string = " a day"
    elif delta.total_seconds() > 5400:
        string = str(round(delta.total_seconds() / 3600)) + " hours"
    elif delta.total_seconds() > 3500:
        string = " an hour"
    elif delta.total_seconds() > 90:
        string = str(round(delta.total_seconds() / 60)) + " minutes"
    elif delta.total_seconds() > 50:
        string = " a minute"
    else:
        string = str(round(delta.total_seconds())) + " seconds"
    string = string + " ago" if past else "in " + string
    return string


@app.template_filter()
def dt_format(dt) -> str:
    """Returns a string formatted like 'on 10 Apr at 10:30' or 'today at 10:30'"""
    dt = localize(dt)
    n = localize(now())

    if not dt.year == n.year:
        f = " on %d %b %Y at %H:%M"
    elif not dt.day == n.day:
        f = " on %d %b at %H:%M"
    else:
        f = " today at %H:%M"

    return dt.strftime(f)


@app.template_filter()
def dt_all(dt) -> str:
    """Combines dt_format() and dt_from_now() like 'today at 10:30 (in 2 hours)'"""
    return f'{dt_format(dt)} ({dt_from_now(dt)})'
