from app import db
import datetime

class ButtonPressLog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=True)
  user = db.relationship('User')
  context_session_id = db.Column(db.Integer, db.ForeignKey('context_session.id'))
  context_session = db.relationship('ContextSession')
