class SentinelAuth:
    @staticmethod
    def get_project_id():
        import os
        return os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")

    @staticmethod
    def get_firestore():
        import firebase_admin
        from firebase_admin import firestore
        
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()
            
        return firestore.client()
        
    @staticmethod
    def init_vertex():
        import vertexai
        import os
        project = SentinelAuth.get_project_id()
        location = os.getenv("GCP_REGION", "us-central1")
        if project:
            vertexai.init(project=project, location=location)
