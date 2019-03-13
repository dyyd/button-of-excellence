from app import db
import datetime

group_user = db.Table('group_users',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    users = db.relationship('User', secondary =group_user, backref = db.backref('groups'))

    def to_dict(self):
        return {
          'id': self.id,
          "description": self.description,
          "users": [row.to_dict() for row in self.users]
        }
