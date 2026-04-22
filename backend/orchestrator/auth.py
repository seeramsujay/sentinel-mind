import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()


class SentinelAuth:
    _db = None
    _project_id = None

    @classmethod
    def get_project_id(cls) -> str:
        if cls._project_id is None:
            cls._project_id = os.getenv("GCP_PROJECT_ID", "sentinelmind")
        return cls._project_id

    @classmethod
    def get_firestore(cls):
        if cls._db is None:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
            if os.path.exists(cred_path):
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {"projectId": cls.get_project_id()})
            else:
                if not firebase_admin._apps:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {"projectId": cls.get_project_id()})
            cls._db = firestore.client()
        return cls._db

    @classmethod
    def init_vertex(cls):
        project = os.getenv("GCP_PROJECT_ID", "sentinelmind")
        location = os.getenv("GCP_REGION", "us-central1")
        try:
            import vertexai
            vertexai.init(project=project, location=location)
        except Exception as e:
            print(f"[SentinelAuth] Vertex AI init skipped — may not be needed in this module: {e}")