from app import db
import datetime

class GroupUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  user = db.relationship('User')
  group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
  group = db.relationship('Group')
