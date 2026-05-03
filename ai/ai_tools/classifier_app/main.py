from fastapi import FastAPI
from classifiers import LinearSVC
from controllers import classify_routers

app = FastAPI()

app.state.classifier = LinearSVC()
app.include_router(classify_routers)