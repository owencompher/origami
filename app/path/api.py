from flask import Blueprint, redirect, request, url_for
from flask_login import current_user
from discord_interactions import verify_key_decorator
from pprint import pp
from config import DISCORD_PUBLIC_KEY
from app import sock, lm, now
from models import User, Queuee
from commands import commands

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/', methods=['POST'])
@verify_key_decorator(DISCORD_PUBLIC_KEY)
def ping():
    interaction = request.get_json()
    if not interaction: return 0
    pp(interaction)

    if interaction['type'] == 1:
        return {'type': 1}
    elif interaction['type'] == 2:
        return commands[interaction['data']['name']](interaction)
    elif interaction['type'] == 3:
        return commands[interaction['data']['custom_id']](interaction)

    return {'type': 0}


@bp.route('/speakers/join', methods=['POST'])
def speakers_join(error=None): 
    if not current_user.is_authenticated: return redirect(url_for('root.login', next=request.args.get('next')))
    note = request.form['note']
    queuee = Queuee.create(user=current_user, note=note, entered=now())
    queuee.save()
    print(f"{now()}: {current_user} joined queue")
    sock.emit('update')

    return redirect(url_for('speakers.list'))


@bp.route('/speakers/skip', methods=['POST'])
def speakers_skip(error=None): 
    if not current_user.is_authenticated or not current_user.admin: return lm.unauthorized()
    queue = Queuee.select(Queuee, User).join(User).order_by(Queuee.entered)
    if queue: 
        print(f"{now()}: {queue[0].user}'s turn ended by {current_user}")
        queue[0].delete_instance()
        sock.emit('update')

    return redirect(url_for('speakers.list'))
