import os
import datetime
from flask import Flask, render_template, request,redirect
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

#Filters for template
@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """Convert a datetime to a different format."""
    return value.strftime(format)

app.jinja_env.filters['datetimefilter'] = datetimefilter

@app.template_filter()
def unique_length(entries):
    """Convert a datetime to a different format."""
    users = [entry.user for entry in entries]
    return len(set(users))

app.jinja_env.filters['unique_length'] = unique_length


@app.route('/')
def home():
    return redirect("/sessions", code=302)
    # return render_template('index.html')


@app.route('/button', methods=['GET'])
def register_button_press():
  # TODO: User check maybe? Maybe allow users that are not present
  user_id = request.args['id']
  user = User.query.filter_by(id=user_id).first()
  sessions = [session for group in user.groups for session in group.sessions if not session.end_time]
  print(sessions)
  print([group.sessions for group in user.groups])
  if len(sessions) > 0:
    log_entry = ButtonPressLog(user_id=user_id, context_session=sessions[0])
  else:
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
  return render_template('users.html', users=users, host_url=app.config['HOST'])

@app.route('/users/test')
def test_users():
  users = User.query.all()
  return render_template('users.html', users=users, testing=True, host_url=app.config['HOST'])

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
    group_id=request_json['groupId'],
    description = request_json['description']
  )
  db.session.add(session)
  open_sessions = [session for session in ContextSession.query.filter_by(group_id=request_json['groupId']).all() if not session.end_time]
  open_sessions.remove(session)

  for session in open_sessions:
    session.end_time = datetime.datetime.now()
  db.session.commit()
  return "%d" % session.id, 200

@app.route('/sessions/<id>', methods=['GET'])
def view_session(id):
  session = ContextSession.query.filter_by(id=id).first()
  entries = ButtonPressLog.query.filter_by(context_session_id=id).all()
  users_raw = [entry.user for entry in entries]
  users = []
  for user in users_raw:
    if user not in users:
      users.append(user)
  return render_template('session.html', users=users, id=id)

@app.route('/sessions/<id>', methods=['PUT'])
def end_sessions(id):
  session = ContextSession.query.get(id)
  session.end_time = datetime.datetime.now()
  db.session.commit()
  return "OK", 200

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
