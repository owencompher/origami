from flask import Blueprint, redirect, render_template, request, url_for, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import now, sock, lm
from models import User, Queuee, Var

bp = Blueprint('speakers', __name__, url_prefix='/speakers')


@bp.route('/')
def list(): 
    queue = Queuee.select(Queuee, User).join(User).order_by(Queuee.entered)
    topic = Var.get_by_id('topic').value
    started = datetime.strptime(Var.get_by_id('speaker_started').value, '%Y-%m-%d %H:%M:%S')
    #   except: started = now()
    return render_template('speakers/list.html', queue=queue, topic=topic, started=started)


@bp.route('/join', methods=['POST'])
@login_required
def join():
    note = request.form['note'] if request.method == 'POST' else request.query_string
    queuee = Queuee.create(user=current_user, note=note, entered=now())
    queuee.save()
    print(f"{now()}: {current_user} joined queue")
    sock.emit('update')

    return redirect(url_for('speakers.list'))


@bp.route('/next', methods=['GET', 'POST'])
@login_required
def next():
    if request.method == 'POST':
        queue = Queuee.select(Queuee, User).join(User).order_by(Queuee.entered)
        if not queue: return abort(500)
        if not (current_user.admin or current_user == queue[0].user): return lm.unauthorized()

        if queue: 
            print(f"{now()}: {queue[0].user}'s turn ended by {current_user}")
            queue[0].delete_instance()
            Var.replace(key='speaker_started', value=now()).execute()
            sock.emit('update')

    elif request.method == 'GET':
        return Queuee.select(Queuee, User).join(User).order_by(Queuee.entered)[0].user.username

    return redirect(url_for('speakers.list'))


@bp.route('/topic', methods=['GET', 'POST'])
@login_required
def topic():
    if request.method == 'POST':
        if not current_user.admin: return lm.unauthorized()
        topic = request.form['topic']
        Var.replace(key='topic', value=topic).execute()
        print(f"{now()}: {current_user} changed topic to \"{topic}\"")
        sock.emit('update')

    return redirect(url_for('speakers.list'))
