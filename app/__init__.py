from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
import logging
# I don't know where logging will go right now!

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)

from app import routes
