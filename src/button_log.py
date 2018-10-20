from app import db

class ButtonPressLog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  time = db.Column(db.DateTime, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
