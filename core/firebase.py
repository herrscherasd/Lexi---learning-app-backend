import firebase_admin
from firebase_admin import credentials

from core.config import settings

def initialize_firebase():
    if firebase_admin._apps:
        return

    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)