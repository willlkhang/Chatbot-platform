from flask import Flask
from flask_sqlalchemy import SQLAlchemy

core = Flask(__name__)
core.config['SECRET_KEY'] = "144e9534a9f468be7a8d97d80fdcb25c"
core.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(core)

from ai_tools import routes