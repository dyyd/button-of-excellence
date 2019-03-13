from app import db
import datetime


class ButtonPressLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=True)
    user = db.relationship('User', backref=db.backref('button_presses', lazy=True))
    context_session_id = db.Column(db.Integer, db.ForeignKey('context_session.id'))
    context_session = db.relationship('ContextSession', backref=db.backref('entries', lazy=True))

    def to_dict(self):
        return {
            'time': self.time.isoformat(),
            "user": self.user.to_dict(),
        }
