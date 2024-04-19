from app import app, db, lm
from models import User, Queuee, Poll, Option, Vote, Var
from path import root, auth, speakers, polls, api
import oauth
import filters  # is unused in main but nescessary to register template filters

app.register_blueprint(root.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(speakers.bp)
app.register_blueprint(polls.bp)
app.register_blueprint(oauth.bp)
app.register_blueprint(api.bp)


def create_tables():
    db.database.create_tables([User, Queuee, Poll, Option, Vote, Var], safe=True)


if __name__ == '__main__':
    lm.init_app(app)
    app.run()
