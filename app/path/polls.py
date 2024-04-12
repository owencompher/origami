from flask import Blueprint, redirect, render_template, request, abort, url_for
from flask_peewee.utils import get_object_or_404
from flask_login import current_user
from app import lm, now
from models import Poll, Option, Vote

bp = Blueprint('polls', __name__, url_prefix='/polls')


@bp.route('/')
def list():
    polls = [poll for poll in Poll.select().order_by(Poll.created.desc())]

    for poll in polls:  # these values are also to sort by alpha
        poll.status = "open"
        if now() < poll.opens: poll.status = "early"
        if poll.closes and now() > poll.closes: poll.status = "closed"

    polls.sort(key=lambda p: p.status, reverse=True)
    #   todo: filtering

    return render_template('polls/list.html', polls=polls, title="polls")


@bp.route('/<int:id>')
def poll(id, error=None):
    poll = get_object_or_404(Poll.select(Poll).where(Poll.id == id))
    poll.options = [option for option in poll.options]
    poll.flags = poll.flags()

    poll.status = "open"
    if now() < poll.opens: poll.status = "early"
    if poll.closes and now() > poll.closes: poll.status = "closed"

    votes = []
    if current_user.is_authenticated:
        options = Option.select(Option.id).where(Option.poll == poll)
        votes = Vote.select(Vote).where((Vote.option.in_(options)) & (Vote.user == current_user))

    votes = [vote.option.id for vote in votes]
    return render_template('polls/view.html', poll=poll, error=error, votes=votes)


@bp.route('/<int:id>/vote', methods=('GET', 'POST',))
def vote(id):
    if request.method == 'GET': return redirect(url_for('polls.poll', id=id))

    if not current_user.is_authenticated: return lm.unauthorized()

    poll = get_object_or_404(Poll.select().where(Poll.id == id))
    poll.flags = poll.flags()

    if now() < poll.opens or (poll.closes and now() > poll.closes): return abort(500)

    options = Option.select(Option.id).where(Option.poll == poll)
    Vote.delete().where((Vote.option.in_(options)) & (Vote.user == current_user)).execute()

    if poll.flags['single']:
        if not Option.get_or_none(request.form['a']): return abort(500)
        Vote.create(user=current_user, option=request.form['a'])

    else:
        for vote in request.form:
            if not Option.get_or_none(vote): return abort(500)
        for vote in request.form:
            Vote.create(user=current_user, option=vote)

    for op in options:
        option = Option.get_by_id(op)
        option.count = option.count_votes()
        print(option)
        option.save()

    return redirect(url_for('polls.poll', id=id))
