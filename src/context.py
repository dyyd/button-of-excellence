from app import db

class Context(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True, nullable=False)

  def __repr__(self):
    return '<Context %d %r>' % (self.id, self.name) # TODO: List all other values
