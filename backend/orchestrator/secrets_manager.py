from google.cloud import secretmanager
from .auth import SentinelAuth

class SentinelSecrets:
    """Manages secure retrieval of API keys from Google Cloud Secret Manager."""
    
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = secretmanager.SecretManagerServiceClient()
        return cls._client

    @classmethod
    def get_secret(cls, secret_id, version_id="latest"):
        """Retrieves a secret from Secret Manager."""
        project_id = SentinelAuth.get_project_id()
        if not project_id:
            # Fallback to env variable if project ID not set
            import os
            return os.getenv(secret_id.upper())

        client = cls.get_client()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        try:
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error accessing secret {secret_id}: {e}")
            # Fallback to environment variable
            import os
            return os.getenv(secret_id.upper())
