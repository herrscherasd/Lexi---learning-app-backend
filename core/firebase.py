import json

import firebase_admin
from firebase_admin import credentials

from core.config import settings

def initialize_firebase():
    if firebase_admin._apps:
        return

    if settings.FIREBASE_CREDENTIALS_JSON:
        cred = credentials.Certificate(
            json.loads(settings.FIREBASE_CREDENTIALS_JSON)
        )
        firebase_admin.initialize_app(cred)
