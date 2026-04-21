import os
import firebase_admin
from firebase_admin import credentials, firestore
import vertexai
from dotenv import load_dotenv

load_dotenv()

class SentinelAuth:
    """Handles authentication for GCP and Firebase services."""
    
    _db = None
    _project_id = None

    @classmethod
    def get_firestore(cls):
        if cls._db is None:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
            if not os.path.exists(cred_path):
                # Fallback to default credentials if running in GCP
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
            else:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
            cls._db = firestore.client()
        return cls._db

    @classmethod
    def init_vertex(cls):
        project = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_REGION", "us-central1")
        if project:
            vertexai.init(project=project, location=location)
        else:
            # Attempt auto-init
            vertexai.init()

    @classmethod
    def get_project_id(cls):
        if not cls._project_id:
            cls._project_id = os.getenv("GCP_PROJECT_ID")
        return cls._project_id
