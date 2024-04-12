from flask import (
    Blueprint, session, redirect, render_template, request, Response
)
from flask_dance.contrib.discord import discord
from models import *

bp = Blueprint('root', __name__)


@bp.route('/')
def index(): return render_template('base.html')


@bp.route('/test')
def test():
    r = discord.get('/api/users/@me')
    if r.ok:
        return r.text
    else:
        return redirect(url_for('root.index'))


@bp.route('/set_tz', methods=['POST'])
def set_timezone():
    """Get timezone from the browser and store it in the session object."""
    timezone = request.data.decode('utf-8')
    print(f"set a timezone to {timezone}")
    session['timezone'] = timezone
    return ""
