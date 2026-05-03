import uvicorn
from fastapi import FastAPI
from classifiers import LinearSVC
from controllers import classify_routers, db_routers
from databases import SQLiteDB


app = FastAPI()

app.state.classifier = LinearSVC()
app.state.db = SQLiteDB()

app.include_router(classify_routers)
app.include_router(db_routers)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8011, reload=True)