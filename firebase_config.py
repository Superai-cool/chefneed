import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Use FIREBASE_KEY_JSON env var (stringified JSON) instead of file
firebase_key = os.environ.get("FIREBASE_KEY_JSON")
cred = credentials.Certificate(json.loads(firebase_key))

firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})
