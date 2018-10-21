from app import db
import datetime

class ContextSession(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  # TODO: Add name here or some better identifier maybe?
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
  end_time = db.Column(db.DateTime, nullable=True) # TODO: Need to set this when session ends!
  context_id = db.Column(db.Integer, db.ForeignKey('context.id'))
  context = db.relationship('Context')
  group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
  group = db.relationship('Group', backref=db.backref('sessions', lazy=True))
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  owner = db.relationship('User', backref=db.backref('session', lazy=True))
