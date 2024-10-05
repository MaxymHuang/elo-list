from flask import Flask
from flask_session import Session
import os
app = Flask(__name__)


# Use the filesystem to store session data
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = True

Session(app)

from app import routes
