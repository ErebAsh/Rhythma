import firebase_admin
from firebase_admin import firestore, credentials
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

# ─── Initialize Firebase (only once) ──────────────────────────────────────
def initialize_firebase():
    if firebase_admin._apps:
        return

    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        return

    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        return

    raise ValueError(
        "Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_JSON "
        "or FIREBASE_SERVICE_ACCOUNT_PATH in .env"
    )

initialize_firebase()
db = firestore.client()

class UserService:
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        now = datetime.utcnow()
        user_data["created_at"] = now
        user_data["updated_at"] = now
        doc_ref = db.collection("users").add(user_data)
        return doc_ref[1].id

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        users = db.collection("users").where("username", "==", username).limit(1).stream()
        for user in users:
            data = user.to_dict()
            data["id"] = user.id
            return data
        return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        users = db.collection("users").where("email", "==", email).limit(1).stream()
        for user in users:
            data = user.to_dict()
            data["id"] = user.id
            return data
        return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        update_data["updated_at"] = datetime.utcnow()
        doc_ref = db.collection("users").document(user_id)
        doc_ref.update(update_data)
        return True