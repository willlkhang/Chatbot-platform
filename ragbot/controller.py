import os #import os for interacting with the env
import logging #import this to output status and error message

from flask import Flask # this is for flask server which a backend server
from flask_restful import Resource, Api, reqparse #this is flask tools to build restful APIs
from flask_cors import CORS #this allows web browsers to make request to this api from different domain.

from waitress import serve #this is for production-ready web server python

from handler import service #call services from hanlder (or service) layer because this layer can interact with the database

# configures the root logger for the application
logging.basicConfig(
    level=os.environ.get("RAGBOT_LOG_LEVEL", "INFO").upper(), #log level based on an env, defaulting to INFO
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s - %(message)s", #defines the string format for each log messages
)
#creates a specific logger instance named as below
logger = logging.getLogger("ragbot.controller")

app = Flask(__name__) #init flask application instance, using the current module's name
api = Api(app) # wraps the flask app witht the flask_restful to add API routes
CORS(app) #allow communication to server or application from other domain.

parser = reqparse.RequestParser() #create a resfful resources class to handle incomming client inputs
parser.add_argument("query", type=str, required=True, help="Message cannot be blank") #define a required string arg name query
parser.add_argument("thread_id", type=str, required=False) #same as above but this one is thread_id for chat session.

#defines a restful resources class to handle incoming client inputs
class ClientInput(Resource):
    def post(self): #declare POST API
        args = parser.parse_args() #parse the arg, which comes in JSON body based on the arg define above
        query = args["query"] # extract query value from the parsed arguments
        thread_id = args.get("thread_id") or None #extracts the thread id, defaulting to None (if in guest mode, it is replaced with a temporary id)

        logger.info("Incoming query thread_id=%s len=%d", thread_id, len(query)) #log the information (This helps me debug)
        #normally, when I test from frontend, there is mistake or error in configuring the listening ports.
        #they just don't work

        try: #try blocks to catch any error during AI processing
            result = service.invoke(query, thread_id=thread_id) #call to service layer which interace with the languagde model.
        except Exception:
            # Never leak stack traces to the client; log them server-side.
            logger.exception("Error while processing query (thread_id=%s)", thread_id)
            return {
                "ai": "Sorry, something went wrong. Please try again.", #debug comments
                "sources": [],
            }, 500

        # ``ai`` retained for backwards compatibility with existing clients;
        # ``sources`` is the new structured citations payload.
        return {"ai": result["answer"], "sources": result["sources"]}


api.add_resource(ClientInput, "/api/response") #makeing APIs routes


#home routes or default routs (well I keep it here)
#because sometimes, the server is running on port 5000
#this default rout is spawned, and my teammates actually go to that localhost port and wait.
#therefore, I display it "Go back" here for a reason
@app.route("/")
def home():
    return "<h1>Go back</h1>"

#health check
@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


def _serve(): #helper functions to start the web server
    host = os.environ.get("RAGBOT_HOST", "0.0.0.0") # gets the host IP to bind to, the inside one is the default
    port = int(os.environ.get("RAGBOT_PORT", "5000")) # the port to listen on, defaulting to 5000
    debug = os.environ.get("RAGBOT_DEBUG", "false").lower() in ("1", "true", "yes") #check for debug mode

    if debug:
        logger.warning("Running Flask dev server (debug=True). Do not use in production.")
        app.run(host=host, port=port, debug=True)
        return

    #my teams try to develop concurrency feature which can allows up to 16 people to use at the same time.
    #however, at this stage it seems to be not fully works, but still works.
    threads = int(os.environ.get("RAGBOT_THREADS", "16"))
    connection_limit = int(os.environ.get("RAGBOT_CONNECTION_LIMIT", "200")) #limite max conntion to 200

    logger.info( #logs an infor message that Waitress is starting
        "Starting waitress on %s:%d (threads=%d, connection_limit=%d)",
        host, port, threads, connection_limit,
    )
    serve( #calls the Waittress serve function
        app, #passes the application to be served
        host=host, #set the host
        port=port, #set port
        threads=threads, #set thread
        connection_limit=connection_limit, #set default connection limit
        channel_timeout=int(os.environ.get("RAGBOT_CHANNEL_TIMEOUT", "120")), #this is how long an idle connection is kept alive
    )


if __name__ == "__main__":
    _serve()
