from flask import Blueprint, redirect, request, url_for
from flask_login import current_user
from app import sock, lm, now
from models import User, Queuee

bp = Blueprint('api', __name__, url_prefix='/api')


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
