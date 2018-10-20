import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['HOST'] = os.environ['HOST']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # TODO: Look into it: https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
db = SQLAlchemy(app)

from user import User
from button_log import ButtonPressLog

@app.route('/')
def home():
    return render_template('index.html')
  # TODO: Return index page with log of button presses


@app.route('/button', methods=['GET'])
def register_button_press():
  # TODO: User check maybe? Maybe allow users that are not present
  user_id = request.args['id']
  log_entry = ButtonPressLog(user_id=user_id)
  db.session.add(log_entry)
  db.session.commit()
  # TODO: Check that it was stored successfully
  return "OK", 200

@app.route('/log')
def view_log():
  # TODO: Add support for requesting specific part of log
  log_entries = ButtonPressLog.query.all()
  return render_template('log.html', entries=reversed(log_entries))

@app.route('/users', methods=['POST'])
def create_user():
  # TODO: check if username in use
  user = User(username= request.args['name'])
  db.session.add(user)
  db.session.commit()
  return "%d" % user.id, 200

@app.route('/users')
def list_users():
  users = User.query.all()
  return render_template('users.html', users=users, host_url=app.config['HOST'])

@app.route('/users/test')
def list_users_with_test():
  users = User.query.all()
  return render_template('users.html', users=users, testing=True, host_url=app.config['HOST'])

if __name__ == '__main__':
  app.run()
