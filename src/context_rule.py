import enum
from app import db

class ContextRuleTypeEnum(enum.Enum):
  visibility = 1
  rounds = 2
  notification = 3
  representation = 4
  interaction = 5


class ContextRule(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True, nullable=False)
  active = db.Column(db.Boolean, default=False)
  context_rule_type = db.Column(db.Enum(ContextRuleTypeEnum))
  context_id = db.Column(db.Integer, db.ForeignKey('context.id'))
  context = db.relationship('Context')
