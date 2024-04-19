from flask import Flask
from flask_peewee.db import Database
from flask_socketio import SocketIO
from flask_login import LoginManager
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import config

app = Flask(__name__, template_folder='template')
app.config.from_object(config)
app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

lm = LoginManager(app)
lm.login_view = 'auth.login'
db = Database(app)
sock = SocketIO(app, cors_allowed_origins=config.WEB_URL, ping_interval=(60, 20), ping_timeout=15)


def now() -> datetime:
    """Get current time in UTC, timezone-naive"""
    return datetime.utcnow().replace(microsecond=0)
