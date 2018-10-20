import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from user import User
from button_log import ButtonPressLog

@app.route('/')
def home():
  return "Hello world!"
  # TODO: Return index page with log of button presses


@app.route('/button/')
def register_button_press():
  return ("In development!", 404)

if __name__ == '__main__':
  app.run()
