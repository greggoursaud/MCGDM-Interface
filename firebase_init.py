import pyrebase
from config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)

def get_firebase_auth():
    return firebase.auth()

def get_firebase_db():
    return firebase.database()