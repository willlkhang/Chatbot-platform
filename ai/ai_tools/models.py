from ai_tools import db

class Material(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)
    
