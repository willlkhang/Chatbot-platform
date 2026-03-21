from flask import request, jsonify
from ai_tools import core
from ai_tools.forms import MaterialForm


# allows people to create data on the database
@core.route("/create", methods=['POST'])
def create():
    raw_data = request.get_json(silent=True)
    
    print(raw_data)
    form = MaterialForm(**raw_data)
    
    if form.validate():
        return jsonify({'condition': [form.topic.data, form.content.data]})
    else:
        return jsonify({'condition': 'failed'})
    