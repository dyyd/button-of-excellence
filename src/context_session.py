from app import db
import datetime

class ContextSession(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String, nullable=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
  end_time = db.Column(db.DateTime, nullable=True) # TODO: Need to set this when session ends!
  context_id = db.Column(db.Integer, db.ForeignKey('context.id'))
  context = db.relationship('Context')
  group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
  group = db.relationship('Group', backref=db.backref('sessions', lazy=True))
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  owner = db.relationship('User', backref=db.backref('session', lazy=True))

  def toDict(sefl):
    data = self.__dict__
    del data['_sa_instance_state']
    data['participation'] = len(set([entry.user for entry in self.entries])) / len(self.group.users)
    return data
