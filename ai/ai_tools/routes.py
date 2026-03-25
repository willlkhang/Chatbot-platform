from flask import request, jsonify
from ai_tools import core, db
from ai_tools.schema import MaterialSchema
from ai_tools.models import Material
from pydantic import ValidationError


# allows people to create data on the database
@core.route("/create", methods=['POST'])
def create():
    raw_data = request.get_json(silent=True)
    try:
        data = MaterialSchema(**raw_data)
        
        materials = Material(topic=data.topic, content=data.content)

        db.session.add(materials)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except ValidationError as e:
        return jsonify({'status': 'failed',
                        'details': e.errors()}), 400
    