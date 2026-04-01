from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_cors import CORS

import asyncio

from main import run_request

app = Flask(__name__)
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('query', type=str, required=True, help="Message cannot be blank")

aiResponse = {
    'ai': fields.String
}

class ClientInput(Resource):
    @marshal_with(aiResponse)
    def post(self):
        args = parser.parse_args()
        query = args['query']
        rag_output = asyncio.run(run_request(query))

        return {'ai': rag_output}

api.add_resource(ClientInput, '/api/response')

@app.route('/')
def home():
    return '<h1>Go back</h1>'

if __name__ == '__main__':
    app.run(debug=True)