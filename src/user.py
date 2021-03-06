import enum
from app import db


class UserTypeEnum(enum.Enum):
    # TODO: Rethink this!
    Student = 1
    Teacher = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.Enum(UserTypeEnum))

    def __repr__(self):
        return self.username

    def to_dict(self):
        return {
          'id': self.id,
          "username": self.username,
          "type": self.type.name
        }
