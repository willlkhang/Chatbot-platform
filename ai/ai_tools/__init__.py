from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
import joblib

current_dir = Path(__file__).parent
model_pth = current_dir / 'NLP_classifier' / 'linearsvc_pipeline.joblib'

core = Flask(__name__)
core.config['SECRET_KEY'] = "144e9534a9f468be7a8d97d80fdcb25c"
core.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(core)
model  = joblib.load(model_pth)

from ai_tools import routes