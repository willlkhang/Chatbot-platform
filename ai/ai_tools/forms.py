from flask_wtf import FlaskForm
from wtforms.fields import StringField, IntegerField
from wtforms.validators import DataRequired


class MaterialForm(FlaskForm):
    
    topic = IntegerField('topic')
    
    content = StringField('content', 
                            validators=[DataRequired()])
    
