import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['HOST'] = os.environ['HOST']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # TODO: Look into it: https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
db = SQLAlchemy(app)

# TODO: Improve this here, shouldn't be loading everything here!
from user import User, UserTypeEnum
from button_log import ButtonPressLog
from context import Context
from context_rule import ContextRule
from context_session import ContextSession
from group import Group
# from group_user import GroupUser

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
  user = User(username= request.args['name'], type=UserTypeEnum(int(request.args['type'])))
  db.session.add(user)
  db.session.commit()
  return "%d" % user.id, 200

@app.route('/users')
def list_users():
  users = User.query.all()
  return render_template('users.html', users=users)

@app.route('/users/test')
def list_users_with_test():
  users = User.query.all()
  return render_template('users.html', users=users, testing=True)

@app.route('/contexts')
def list_contexts():
  contexts = Context.query.all()
  return render_template('contexts.html', contexts=contexts)

@app.route('/contexts/<id>')
def view_context(id):
  context = Context.query.filter_by(id=id).first()
  print(context)
  return render_template('context.html', context=context)

@app.route('/contexts/new')
def new_context():
  return render_template('new_context.html') # TODO: Pass in possible rules or rule types etc

@app.route('/contexts', methods=['POST'])
def create_context():
  # TODO: Get params from request and construct Context with ContextRules
  context = Context(name= request.args['name'])
  db.session.add(context)
  db.session.commit()
  return "%d" % context.id, 200

@app.route('/sessions')
def list_sessions():
  sessions = ContextSession.query.all()
  contexts = Context.query.all()
  groups = Group.query.all()
  return render_template('sessions.html', sessions=sessions, contexts=contexts, groups=groups)

@app.route('/sessions', methods=['POST'])
def start_sessions():
  # TODO: Create new session based on context chosen
  request_json = request.get_json(force=True)
  session = ContextSession(
    context_id=request_json['contextId'],
    group_id=request_json['groupId']
  )
  db.session.add(session)
  db.session.commit()
  return "%d" % session.id, 200

@app.route('/sessions/<id>', methods=['GET'])
def view_session(id):
  # TODO: Show session info. If not ended show active session info. If ended show overview/statistics
  return "Under construction!", 404

@app.route('/sessions/<id>', methods=['PUT'])
def end_sessions(id):
  # TODO: find session and end it
  return "Under construction!", 404

@app.route('/groups', methods=['POST'])
def create_group():
  request_json = request.get_json(force=True)
  print(request_json)
  group = Group(description = request_json['description'])
  users = User.query.filter(User.id.in_([int(id) for id in request_json['users']])).all()
  [group.users.append(user) for user in users]
  db.session.add(group)
  db.session.commit()
  return "%d" % group.id, 200

@app.route('/groups')
def list_groups():
  groups = Group.query.all()
  users = User.query.all()
  return render_template('groups.html', groups=groups, users=users)

if __name__ == '__main__':
  app.run()
