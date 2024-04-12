from app import app
from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.peewee import ModelView
from flask_login import current_user
from models import User, Queuee, Poll, Option, Vote, Var


class AuthView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=url_for(request.endpoint)))


class IndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=url_for(request.endpoint)))


admin = Admin(app, name="admin", index_view=IndexView())
admin.add_view(AuthView(User))
admin.add_view(AuthView(Queuee))
admin.add_view(AuthView(Poll))
admin.add_view(AuthView(Option))
admin.add_view(AuthView(Vote))
admin.add_view(AuthView(Var))
