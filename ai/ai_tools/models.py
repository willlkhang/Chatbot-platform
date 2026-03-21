from ai_tools import db

class Materials(db.model):
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.Integer, nullable=False)
    content = db.Column(db.StringField, nullable=False)
    
