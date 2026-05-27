import os #import os for interacting with the env
import logging #import this to output status and error message

from flask import Flask # this is for flask server which a backend server
from flask_restful import Resource, Api, reqparse #this is flask tools to build restful APIs
from flask_cors import CORS #this allows web browsers to make request to this api from different domain.

from waitress import serve #this is for production-ready web server python

from handler import service #call services from hanlder (or service) layer because this layer can interact with the database

# configures the root logger for the application
logging.basicConfig(
    level=os.environ.get("RAGBOT_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s - %(message)s",
)
logger = logging.getLogger("ragbot.controller")

app = Flask(__name__)
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument("query", type=str, required=True, help="Message cannot be blank")
parser.add_argument("thread_id", type=str, required=False)


class ClientInput(Resource):
    def post(self):
        args = parser.parse_args()
        query = args["query"]
        thread_id = args.get("thread_id") or None

        logger.info("Incoming query thread_id=%s len=%d", thread_id, len(query))

        try:
            result = service.invoke(query, thread_id=thread_id)
        except Exception:
            # Never leak stack traces to the client; log them server-side.
            logger.exception("Error while processing query (thread_id=%s)", thread_id)
            return {
                "ai": "Sorry, something went wrong. Please try again.",
                "sources": [],
            }, 500

        # ``ai`` retained for backwards compatibility with existing clients;
        # ``sources`` is the new structured citations payload.
        return {"ai": result["answer"], "sources": result["sources"]}


api.add_resource(ClientInput, "/api/response")


@app.route("/")
def home():
    return "<h1>Go back</h1>"


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


def _serve():
    host = os.environ.get("RAGBOT_HOST", "0.0.0.0")
    port = int(os.environ.get("RAGBOT_PORT", "5000"))
    debug = os.environ.get("RAGBOT_DEBUG", "false").lower() in ("1", "true", "yes")

    if debug:
        logger.warning("Running Flask dev server (debug=True). Do not use in production.")
        app.run(host=host, port=port, debug=True)
        return

    threads = int(os.environ.get("RAGBOT_THREADS", "16"))
    connection_limit = int(os.environ.get("RAGBOT_CONNECTION_LIMIT", "200"))

    logger.info(
        "Starting waitress on %s:%d (threads=%d, connection_limit=%d)",
        host, port, threads, connection_limit,
    )
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        connection_limit=connection_limit,
        channel_timeout=int(os.environ.get("RAGBOT_CHANNEL_TIMEOUT", "120")),
    )


if __name__ == "__main__":
    _serve()
