import os

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

@app.route('/healthz')
def healthz():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    host = os.environ.get("RAGBOT_HOST", "0.0.0.0")
    port = int(os.environ.get("RAGBOT_PORT", "5000"))
    debug = os.environ.get("RAGBOT_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)