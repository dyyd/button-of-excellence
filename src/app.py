import os
import datetime
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
# TODO: Proper conf file would be nice!   # os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'] # 'postgresql://localhost:5432/button'
# TODO: Look into it:
#  https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TODO: Improve this here, shouldn't be loading everything here!
from user import User, UserTypeEnum
from button_log import ButtonPressLog
from context import Context
from context_rule import ContextRule
from context_session import ContextSession
from group import Group

# ############# Routes ##############

# ###### HTML routes #######


@app.route('/')
def home():
    return redirect(url_for("new_session"))


@app.route('/log')
def log_viewer():
    # TODO: Refactor so users list is retrieved from API
    log_entries = ButtonPressLog.query.order_by(ButtonPressLog.time.desc()).all()
    return render_template('log.html', entries=log_entries)


@app.route('/users')
def users_list():
    return render_template('users.html')


@app.route('/sessions')
def sessions_list():
    return render_template('sessions.html')


@app.route('/sessions/<uuid>', methods=['GET'])
def view_session(uuid):
    session = ContextSession.query.filter_by(id=uuid).first()
    entries = ButtonPressLog.query.filter_by(context_session_id=uuid).all()
    users_raw = [entry.user for entry in entries]
    users = []
    for user in users_raw:
        if user not in users:
            users.append(user)
    filled_percentage = get_percentage(len(users), len(session.group.users))
    if session.context.id == 2:
        users = []
    return render_template(
        'session.html',
        users=users,
        id=uuid,
        fill=filled_percentage,
        description=session.description,
        active=session.end_time
    )


@app.route('/sessions/new')
def new_session():
    groups = Group.query.all()
    contexts = Context.query.all()
    return render_template('new_session.html', groups=groups, contexts=contexts)


@app.route('/groups')
def groups_list():
    # TODO: Refactor so users list is retrieved from API
    users = User.query.all()
    return render_template('groups.html', users=users)


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
    # TODO: Only return html page, split DB lookup into API endpoint (lookup groups and other values necessary for
    #  statistics table but don't do stats lookup)
    groups = Group.query.all()
    users = []
    for group in groups:
        users = users + group.users
    users = set(users)
    stats = []
    for user in users:
        # find all presses that were with session
        presses = len(
          set(
            [
              press.context_session for press in user.button_presses if press.context_session_id is not None
            ]
          )
        )
        sessions = len(set([session for group in user.groups for session in group.sessions]))
        stats.append((user, presses, sessions, get_percentage(presses, sessions)))
    stats = sorted(stats, key=sorter, reverse=True)
    return render_template('statistics.html', groups=groups, stats=stats)


@app.route('/contexts')
def contexts_list():
    return render_template('contexts.html')


@app.route('/contexts/<uuid>')
def view_context(uu):
    context = Context.query.filter_by(id=uu).first()
    return render_template('context.html', context=context)


@app.route('/contexts/new')
def new_context():
    return render_template('new_context.html')  # TODO: Pass in possible rules or rule types etc


# ####### API routes #######


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


# TODO: /api/v1/users/<uuid> GET  info  # Not necessary ATM
# TODO: /api/v1/users/<uuid> PUT  edit

@app.route('/api/v1/users')
def list_users():
    data = {'users': [row.to_dict() for row in User.query.all()]}
    return jsonify(data)


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    # TODO: Move to separate module
    # TODO: check if username in use
    if not request.args['name']:
        return "Kasutaja nimi on puudu!", 409
    try:
        user = User(username=request.args['name'], type=UserTypeEnum(int(request.args['type'])))
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError as e:
        return "Kasutaja eksisteerib!", 409


@app.route('/api/v1/users/<uuid>', methods=['DELETE'])
def delete_user(uuid):
    entry = User.query.get(uuid)
    db.session.delete(entry)
    db.session.commit()
    return "OK", 200  # TODO: Error handling when entry in use or not found


# ### Sessions ###


@app.route('/api/v1/sessions', methods=['GET'])
def list_sessions():
    data = {'sessions': [row.to_dict() for row in ContextSession.query.order_by(ContextSession.start_time.desc()).all()]}
    return jsonify(data)


@app.route('/api/v1/sessions/<uuid>', methods=['GET'])
def get_session(uuid):
    # TODO: Move db fetching to separate module
    data = {}
    session = ContextSession.query.filter_by(id=uuid).first()
    entries = ButtonPressLog.query.filter_by(context_session_id=uuid).all()

    users_raw = [entry.user for entry in entries]
    users = []
    for user in users_raw:
        if user not in users:
            users.append(user)
    data['filled_percentage'] = get_percentage(len(users), len(session.group.users))
    if session.context.id == 2:
        users = []
    data['users'] = [row.to_dict() for row in users]
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
    open_sessions = [s for s in ContextSession.query.filter_by(group_id=request_json['groupId']).all() if not session.end_time]
    open_sessions.remove(session)

    for s in open_sessions:
        s.end_time = datetime.datetime.utcnow()
    db.session.commit()
    return "%d" % session.id, 200


@app.route('/api/v1/sessions/<uuid>', methods=['PUT'])
def update_session(uuid):
    # TODO: Refactor so it allows for modification as well
    session = ContextSession.query.get(uuid)
    session.end_time = datetime.datetime.utcnow()
    db.session.commit()
    return "OK", 200


@app.route('/api/v1/sessions/<uuid>', methods=['DELETE'])
def delete_session(uuid):
    entry = ContextSession.query.get(uuid)
    db.session.delete(entry)
    db.session.commit()
    return "OK", 200 # TODO: Error handling when entry in use or not found


# ### Groups ###

# TODO: /api/v1/groups/<uuid> GET  info
# TODO: /api/v1/groups/<uuid> PUT  edit


@app.route('/api/v1/groups', methods=['GET'])
def list_groups():
    data = {'groups': [row.to_dict() for row in Group.query.all()]}
    return jsonify(data)


@app.route('/api/v1/groups', methods=['POST'])
def create_group():
    # TODO: Move into separate db module ?
    request_json = request.get_json(force=True)
    if not request_json['description']:
        return "Grupi nimi on puudu!", 409
    if not request_json['users']:
        return "Grupi liikmeid pole valitud!", 409
    group = Group(description = request_json['description'])
    users = User.query.filter(User.id.in_([int(uuid) for uuid in request_json['users']])).all()
    [group.users.append(user) for user in users]
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_dict())


@app.route('/api/v1/groups/<uuid>', methods=['DELETE'])
def delete_group(uuid):
    entry = Group.query.get(uuid)
    db.session.delete(entry)
    db.session.commit
    return "OK", 200 # TODO: Error handling when entry in use or not found


# ### Contexts ###

# TODO: /api/v1/contexts GET  list        # Not necessary ATM
# TODO: /api/v1/contexts/<uuid> GET  info   # Not necessary ATM
# TODO: /api/v1/contexts/<uuid> PUT  edit   # Not necessary ATM
# TODO: /api/v1/contexts/<uuid> DELETE      # Not necessary ATM


@app.route('/api/v1/contexts', methods=['POST'])
def create_context():
    # TODO: Get params from request and construct Context with ContextRules
    context = Context(name= request.args['name'])
    db.session.add(context)
    db.session.commit()
    return "%d" % context.id, 200


# ### Logs ###


@app.route('/api/v1/logs')
def list_log_entries():
    data = {'log_entries': [row.to_dict() for row in ButtonPressLog.query.order_by(ButtonPressLog.time.desc()).all()]}
    # TODO: Add support for requesting specific part of log
    return jsonify(data)


if __name__ == '__main__':
    app.run(threaded=True)
