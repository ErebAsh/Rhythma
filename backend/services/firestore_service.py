import firebase_admin
from firebase_admin import firestore, credentials
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

# ─── Initialize Firebase (only once) ──────────────────────────────────────
def initialize_firebase():
    if firebase_admin._apps:
        return

    # Option 1: JSON string from environment
    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        return

    # Option 2: Path to JSON file
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
        """Create a new user document in Firestore."""
        try:
            now = datetime.now(timezone.utc)
            user_data["created_at"] = now
            user_data["updated_at"] = now
            doc_ref = db.collection("users").add(user_data)
            return doc_ref[1].id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by username."""
        try:
            users = db.collection("users").where("username", "==", username).limit(1).stream()
            for user in users:
                data = user.to_dict()
                data["id"] = user.id
                return data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by email."""
        try:
            users = db.collection("users").where("email", "==", email).limit(1).stream()
            for user in users:
                data = user.to_dict()
                data["id"] = user.id
                return data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by Firestore document ID."""
        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a user document and set updated_at."""
        try:
            update_data["updated_at"] = datetime.now(timezone.utc)
            doc_ref = db.collection("users").document(user_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )