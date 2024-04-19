from flask import url_for
from peewee import *
from flask_login import UserMixin
from app import db, now


class User(db.Model, UserMixin):
    username = CharField(unique=True)
    password = CharField(null=True)
    email = CharField(null=True)
    joined = DateTimeField(default=now())
    admin = BooleanField(default=False)
    editor = BooleanField(default=False)
    duid = CharField(null=True)
    token = TextField(null=True)

    def __str__(self): return self.username

    def link(self): return url_for('auth.user', username=self.username)


class Queuee(db.Model):
    user = ForeignKeyField(User, backref='queuees')
    note = CharField()
    entered = DateTimeField(default=now())


class Poll(db.Model):
    name = CharField()
    description = TextField(null=True)
    owner = ForeignKeyField(User, backref="polls")
    created = DateTimeField()
    opens = DateTimeField()
    closes = DateTimeField(null=True)
    optflags = SmallIntegerField(default=0)

    def flags(self):
        return {
            'single': self.optflags % 2 == 0,
            'hide_votes': self.optflags >> 1 % 2 == 0
        }


class Option(db.Model):
    poll = ForeignKeyField(Poll, backref="options")
    name = CharField()
    description = TextField(null=True)
    count = IntegerField(default=0)

    def count_votes(self): 
        return Vote.select().where(Vote.option == self).count()


class Vote(db.Model):
    user = ForeignKeyField(User, backref="votes")
    option = ForeignKeyField(Option, backref="votes")
    score = IntegerField(default=0)


class Var(db.Model):
    key = CharField(primary_key=True, unique=True)
    value = TextField()
