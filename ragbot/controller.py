from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_cors import CORS

import asyncio

from handler import run_request

app = Flask(__name__)
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('query', type=str, required=True, help="Message cannot be blank")
parser.add_argument('thread_id', type=str, required=False)

aiResponse = {
    'ai': fields.String
}

class ClientInput(Resource):
    @marshal_with(aiResponse)
    def post(self):
        args = parser.parse_args()
        query = args['query']
        thread_id = args.get("thread_id") or None
        rag_output = asyncio.run(run_request(query, thread_id=thread_id))

        return {'ai': rag_output}

api.add_resource(ClientInput, '/api/response')

@app.route('/')
def home():
    return '<h1>Go back</h1>'

if __name__ == '__main__':
    app.run(debug=True)