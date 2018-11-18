import os
import datetime
#import json
from flask import Flask, render_template, request,redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'] # 'postgresql://localhost:5432/button' # TODO: Proper conf file would be nice!   # os.environ['DATABASE_URL']
app.config['HOST'] = os.environ['HOST'] # 'localhost:5000' # TODO: Proper conf file would be nice!  # os.environ['HOST']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # TODO: Look into it: https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
db = SQLAlchemy(app)

# TODO: Improve this here, shouldn't be loading everything here!
from user import User, UserTypeEnum
from button_log import ButtonPressLog
from context import Context
from context_rule import ContextRule
from context_session import ContextSession
from group import Group
from momentjs import momentjs

app.jinja_env.globals['momentjs'] = momentjs

############## Routes ##############

####### HTML routes #######

@app.route('/')
def home():
    return redirect("/sessions/new", code=302) # TODO: Redirect to new Session page

@app.route('/log')
def log_viewer():
  # TODO: Refactor so users list is retrieved from API
  log_entries = ButtonPressLog.query.order_by(ButtonPressLog.time.desc()).all()
  return render_template('log.html', entries=log_entries)

@app.route('/users')
def users_list():
  users = User.query.all() # TODO: Refactor so users list is retrieved from API
  return render_template('users.html', users=users, host_url=app.config['HOST'])

@app.route('/users/test')
def users_testing():
  users = User.query.all() # TODO: Refactor so users list is retrieved from API
  return render_template('users.html', users=users, testing=True, host_url=app.config['HOST'])

@app.route('/sessions')
def sessions_list():
  return render_template('sessions.html')

@app.route('/sessions/<id>', methods=['GET'])
def view_session(id):
  session = ContextSession.query.filter_by(id=id).first()
  entries = ButtonPressLog.query.filter_by(context_session_id=id).all()
  users_raw = [entry.user for entry in entries]
  users = []
  for user in users_raw:
    if user not in users:
      users.append(user)
  filled_percentage = get_percentage(len(users), len(session.group.users))
  if session.context.id == 2:
    users = []
  return render_template('session.html', users=users, id=id, fill=filled_percentage, description= session.description)

@app.route('/sessions/new')
def new_session():
  groups = Group.query.all()
  contexts = Context.query.all()
  return render_template('new_session.html', groups=groups, contexts=contexts)

@app.route('/groups')
def groups_list():
  # TODO: Refactor so users list is retrieved from API
  groups = Group.query.all()
  users = User.query.all()
  return render_template('groups.html', groups=groups, users=users)

# TODO: Move into separate statistics module or sth
def sorter(item):
  return item[3]

# TODO: Move into separate statistics module or sth
def get_percentage(value, total):
  if value == 0 or total == 0:
    result = 0.0
  else:
    result = (value/float(total)) * 100
  return "%.2f" % result

@app.route('/statistics')
def statistics():
  # TODO: Only return html page, split DB lookup into API endpoint (lookup groups and other values necessary for statistics table but don't do stats lookup)
  groups = Group.query.all()
  users = []
  for group in groups:
    users = users + group.users
  users = set(users)
  stats = []
  for user in users:
    # find all presses that were with session
    presses = len(set([press.context_session for press in user.button_presses if press.context_session_id is not None]))
    sessions = len(set([session for group in user.groups for session in group.sessions]))
    stats.append((user, presses, sessions, get_percentage(presses, sessions)))
  stats = sorted(stats, key=sorter, reverse=True)
  return render_template('statistics.html', groups=groups, stats=stats)

@app.route('/contexts')
def contexts_list():
  return render_template('contexts.html')

@app.route('/contexts/<id>')
def view_context(id):
  context = Context.query.filter_by(id=id).first()
  return render_template('context.html', context=context)

@app.route('/contexts/new')
def new_context():
  return render_template('new_context.html') # TODO: Pass in possible rules or rule types etc

####### API routes #######

@app.route('/api/v1/button', methods=['POST'])
def register_button_press():
  # TODO: Move to separate module?
  # TODO: User check maybe? Maybe allow users that are not present
  user_id = request.args['id']
  user = User.query.filter_by(id=user_id).first()
  sessions = [session for group in user.groups for session in group.sessions if not session.end_time]
  if len(sessions) > 0:
    log_entry = ButtonPressLog(user_id=user_id, context_session=sessions[0])
  else:
    log_entry = ButtonPressLog(user_id=user_id)
  db.session.add(log_entry)
  db.session.commit()
  # TODO: Check that it was stored successfully
  return "OK", 200


# TODO: /api/v1/users/<id> GET  info  # Not necessary ATM
# TODO: /api/v1/users/<id> PUT  edit

def filtered(row):
  row_dict = row.__dict__
  del row_dict['_sa_instance_state']
  return row_dict

@app.route('/api/v1/users')
def list_users():
  data = {}
  data['users'] = [ row.toDict() for row in User.query.all()]
  return jsonify(data)

@app.route('/api/v1/users', methods=['POST'])
def create_user():
  # TODO: Move to deparate module
  # TODO: check if username in use
  user = User(username= request.args['name'], type=UserTypeEnum(int(request.args['type'])))
  db.session.add(user)
  db.session.commit()
  return user.toDict()

@app.route('/api/v1/users/<id>', methods=['DELETE'])
def delete_user(id):
  entry = User.query.get(id)
  db.session.delete(entry)
  db.session.commit()
  return "OK", 200 # TODO: Error handling when entrey in use or not found

### Sessions ###

@app.route('/api/v1/sessions', methods=['GET'])
def list_sessions():
  data = {}
  data['sessions'] = [ row.toDict() for row in ContextSession.query.order_by(ContextSession.start_time.desc()).all()]
  return jsonify(data)

@app.route('/api/v1/sessions/<id>', methods=['GET'])
def get_session(id):
  # TODO: Move db fetching to separate module
  data ={}
  data['session'] = [ filtered(row) for row in ContextSession.query.filter_by(id=id).first()]
  data['entries'] = [ filtered(row) for row in ButtonPressLog.query.filter_by(context_session_id=id).all()]
  users_raw = [entry.user for entry in entries]
  users = []
  for user in users_raw:
    if user not in users:
      users.append(user)
  data['filled_percentage'] = get_percentage(len(users), len(session.group.users))
  if session.context.id == 2:
    users = []
  data['users'] = [ row.toDict() for row in users]
  return jsonify(data)

@app.route('/api/v1/sessions', methods=['POST'])
def create_session():
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
    session.end_time = datetime.datetime.utcnow()
  db.session.commit()
  return "%d" % session.id, 200

@app.route('/api/v1/sessions/<id>', methods=['PUT'])
def update_session(id):
  # TODO: Refactor so it allows for modification as well
  session = ContextSession.query.get(id)
  session.end_time = datetime.datetime.utcnow()
  db.session.commit()
  return "OK", 200

@app.route('/api/v1/sessions/<id>', methods=['DELETE'])
def delete_session(id):
  entry = ContextSession.query.get(id)
  db.session.delete(entry)
  db.session.commit()
  return "OK", 200 # TODO: Error handling when entrey in use or not found

### Groups ###

# TODO: /api/v1/groups/<id> GET  info
# TODO: /api/v1/groups/<id> PUT  edit

@app.route('/api/v1/groups', methods=['GET'])
def list_groups():
  data = {}
  data['groups'] = [ filtered(row) for row in Group.query.all()]
  return jsonify(data)

@app.route('/api/v1/groups', methods=['POST'])
def create_group():
  # TODO: Move into separate db module ?
  request_json = request.get_json(force=True)
  group = Group(description = request_json['description'])
  users = User.query.filter(User.id.in_([int(id) for id in request_json['users']])).all()
  [group.users.append(user) for user in users]
  db.session.add(group)
  db.session.commit()
  return jsonify(group)

@app.route('/api/v1/groups/<id>', methods=['DELETE'])
def delete_group(id):
  entry = Group.query.get(id)
  db.session.delete(entry)
  db.session.commit
  return "OK", 200 # TODO: Error handling when entrey in use or not found

### Contexts ###

# TODO: /api/v1/contexts GET  list        # Not necessary ATM
# TODO: /api/v1/contexts/<id> GET  info   # Not necessary ATM
# TODO: /api/v1/contexts/<id> PUT  edit   # Not necessary ATM
# TODO: /api/v1/contexts/<id> DELETE      # Not necessary ATM

@app.route('/api/v1/contexts', methods=['POST'])
def create_context():
  # TODO: Get params from request and construct Context with ContextRules
  context = Context(name= request.args['name'])
  db.session.add(context)
  db.session.commit()
  return "%d" % context.id, 200

### Logs ###

@app.route('/api/v1/logs')
def list_log_entries():
  data = {}
  data['log_entries'] = [ filtered(row) for row in ButtonPressLog.query.order_by(ButtonPressLog.time.desc()).all()]
  # TODO: Add support for requesting specific part of log
  return jsonify(data)

if __name__ == '__main__':
  app.run()
