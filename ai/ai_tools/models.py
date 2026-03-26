from ai_tools import db

class Material(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Material {self.id} - Topic {self.topic}>"