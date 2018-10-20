from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:////localhost:'
# db = SQLAlchemy(app)


# class User(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   username = db.Column(db.String(80), unique=True, nullable=False)

#   def __repr__(self):
#     return '<User %d %r>' % self.id, self.username

# class ButtonPressLog(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   time = db.Column(db.DateTime, nullable=False)
#   user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
#         nullable=False)

@app.route('/')
def home():
  return "Hello world!"
  # TODO: Return index page with log of button presses


@app.route('/button/')
def register_button_press():
  return ("In development!", 404)

if __name__ == '__main__':
  app.run()
