from flask import request, jsonify
from ai_tools import core, db, model
from ai_tools.schema import MaterialSchema, GetMaterialSchema, ClassifySchema
from ai_tools.models import Material
from pydantic import ValidationError

"""
I know these are coupled but meh.
"""

# allows people to create data on the database
@core.route("/create", methods=['POST'])
def create():
    raw_data = request.get_json(silent=True)
    if not raw_data:
        return jsonify({'status': 'failed',
                        'details': 'None field entered.'}), 400
    try:
        data = MaterialSchema(**raw_data)
        
        materials = Material(**data.model_dump())

        db.session.add(materials)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except ValidationError as e:
        return jsonify({'status': 'failed',
                        'details': e.errors()}), 400

# allows people to get all data matching a specific topic
@core.route("/get", methods=['POST'])
def get_material():
    raw_data = request.get_json(silent=True)
    
    if not raw_data:
        return jsonify({'status': 'failed',
                        'details': 'None field entered.'}), 400
    try:
        data = GetMaterialSchema(**raw_data)
        
        # Search the database for everything matching this topic
        materials = Material.query.filter_by(topic=data.topic).all()

        if not materials:
            return jsonify({'status': 'failed',
                            'details': 'No materials found for this topic.'}), 404
        
        # Package up all the matches into a list
        results = [{'id': m.id, 'topic': m.topic, 'content': m.content} for m in materials]

        return jsonify({'status': 'success', 'data': results})
    except ValidationError as e:
        return jsonify({'status': 'failed',
                        'details': e.errors()}), 400

# allows people to send content to the NLP model for prediction
@core.route("/classify", methods=['POST'])
def classify():
    raw_data = request.get_json(silent=True)
    
    if not raw_data:
        return jsonify({'status': 'failed',
                        'details': 'None field entered.'}), 400
    try:
        data = ClassifySchema(**raw_data)
        
        if model is None:
            return jsonify({'status': 'failed',
                            'details': 'Model not loaded.'}), 503

        # Run the model using 'content' instead of 'text'
        prediction = model.predict([data.content])
        
        return jsonify({'status': 'success', 'prediction': str(prediction[0])})
    
    except ValidationError as e:
        return jsonify({'status': 'failed',
                        'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'status': 'failed',
                        'details': str(e)}), 500