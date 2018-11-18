import enum
from app import db


class UserTypeEnum(enum.Enum, dict):
  def __init__(self, fname):
      dict.__init__(self, fname=fname)
  #TODO: Rethink this!
  Student = 1
  Teacher = 2

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  type = db.Column(db.Enum(UserTypeEnum))

  def __repr__(self):
    return self.username
