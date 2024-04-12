from flask import session, request
from flask_dance.contrib.discord import make_discord_blueprint
from flask_dance.consumer.storage import BaseStorage
from flask_dance.consumer import oauth_authorized, oauth_before_login
from flask_login import login_user, current_user
import ast
from config import discord_client_secret
from models import *


class InUserStorage(BaseStorage):
    def get(self, blueprint):
        if current_user.is_authenticated and current_user.token:
            return ast.literal_eval(current_user.token)
        else:
            return session.get('oauth_token')

    def set(self, blueprint, token):
        if current_user.is_authenticated:
            current_user.token = token
            r = blueprint.session.get('/api/users/@me')
            if r.ok: current_user.duid = r.json()['id']
            current_user.save()
        session['oauth_token'] = token

    def delete(self, blueprint):
        if current_user.is_authenticated:
            del current_user.token
            current_user.save()
        del session['oauth_token']


bp = make_discord_blueprint(
    client_id='1225823464586481875',
    client_secret=discord_client_secret,
    scope=('identify', 'guilds'),
    storage=InUserStorage(),
    #    prompt=None
)
bp.authorization_url_params["prompt"] = "none"


@oauth_before_login.connect
def oauth_out_handler(blueprint, url): session['register'] = 'register' in request.args


@oauth_authorized.connect
def oauth_in_handler(blueprint, token):
    if not token: return False
    if 'oauth_token' in session: del session['oauth_token']

    r = blueprint.session.get('/api/users/@me')

    if r.ok:
        uid = r.json()['id']
    else:
        return False

    user = User.get_or_none(User.duid == uid)

    if session['register'] and not user and not current_user.is_authenticated:
        u = r.json()['username']

        def username(n):
            return u + (str(n) if n > 0 else '')

        uniq = 0  # repeatedly add a higher number to the end until it is unique
        while User.get_or_none(User.username == username(uniq)): uniq += 1
        user = User(username=username(uniq), joined=now(), duid=uid, token=token)
        user.save()

    if user:
        login_user(user)

    else:
        return url_for('root.index')
