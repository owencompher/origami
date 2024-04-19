from flask import (
    Blueprint, redirect, render_template, request, url_for
)
from flask_login import current_user
from pathlib import Path
from markdown import markdown
from app import lm
from config import WIKI_DIR

bp = Blueprint('wiki', __name__, url_prefix="/wiki")


@bp.route('/')
@bp.route('/<path:path>')
def wiki(path='_index'):
    p = Path(WIKI_DIR, path)
    if not p.exists(): return f"{path} does not exist in wiki.", 404 # <a href={url_for('wiki.create', path=path)}>create page {p.name}?</a>", 404
    if p.is_dir(): p = Path(p, '_index')

    directory = ''.join([build_dir(path, p) for path in filter(lambda x: x.name != '_index', sorted(Path(WIKI_DIR).iterdir(), key=lambda pa: pa.stem))])

    return render_template('wiki/view.html', page=markdown(p.read_text()), directory=directory, path=path)

@bp.route('/edit')
@bp.route('/edit/<path:path>', methods=['GET', 'POST'])
def edit(path='_index'):
    if not (current_user.is_authenticated and current_user.editor): return lm.unauthorized()

    p = Path(WIKI_DIR, path)
    if not p.exists(): return f"{path} does not exist in wiki.", 404 # <a href={url_for('wiki.create', path=path)}>create page {p.name}?</a>", 404
    if p.is_dir(): p = Path(p, '_index')
    if not p.exists(): return redirect(url_for('wiki.wiki', path=path))

    if request.method == 'POST':
        text = request.form['text']
        p.write_text(text)
        return redirect(url_for('wiki.wiki', path=path))

    directory = ''.join([build_dir(path, p) for path in filter(lambda x: x.name != '_index', sorted(Path(WIKI_DIR).iterdir(), key=lambda pa: pa.stem))])

    return render_template('wiki/edit.html', page=p.read_text(), directory=directory, path=path)


@bp.route('/create/<path:path>')
def create(path):
    # todo: fix case of file in a new directory
    # todo: allow changes to name, location when creating
    if not (current_user.is_authenticated and current_user.editor): return lm.unauthorized()

    if Path(WIKI_DIR, path).exists(): return redirect(url_for('wiki.wiki', path=path))

    Path(WIKI_DIR, path).touch()
    return redirect(url_for('wiki.edit', path=path))

# todo: add deleting, removing/renaming files


def build_dir(path, cur):
    if path.is_dir():
         return f"<details {'open' if cur.is_relative_to(path) else ''}><summary>" + \
               (f"<a href='/wiki/{path.relative_to(WIKI_DIR).as_posix()}'>" if Path(path, '_index').exists() else '') + \
                f"{path.stem}</summary>" + \
                 ''.join([build_dir(path, cur) for path in filter(lambda x: x.name != '_index', sorted(path.iterdir(), key=lambda pa: pa.stem))]) + \
                 "</details>"
    elif path.is_file():
        return f"<a href='/wiki/{path.relative_to(WIKI_DIR).as_posix()}'>{path.stem}</a><br>"
