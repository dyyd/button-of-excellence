import enum
import json
from app import db


class UserTypeEnum(enum.Enum):
  #TODO: Rethink this!
  Student = 1
  Teacher = 2

class Kasutaja(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  type = db.Column(db.Enum(UserTypeEnum))

  def __repr__(self):
    return self.username

  def toJson(self):
    data = {}
    data['id'] = self.id
    data['username'] = self.username
    data['type'] = self.type.name
    return json.dumps(data)
