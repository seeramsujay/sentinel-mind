import sys
import types
from unittest.mock import MagicMock

def make_mock_pkg(name):
    m = types.ModuleType(name)
    m.__path__ = []
    sys.modules[name] = m
    return m

for pkg in ["firebase_admin", "google", "google.cloud", "vertexai"]:
    if pkg not in sys.modules:
        make_mock_pkg(pkg)

for mod in [
    "firebase_admin.firestore",
    "firebase_admin.credentials",
    "google.cloud.firestore",
    "google.cloud.aiplatform",
    "google.cloud.secretmanager",
    "vertexai.generative_models",
    "vertexai.preview",
    "vertexai.preview.generative_models",
    "googlemaps",
]:
    sys.modules[mod] = MagicMock()
    # also set on parent
    parts = mod.split(".")
    parent = sys.modules[parts[0]]
    for p in parts[1:]:
        if not hasattr(parent, p):
            setattr(parent, p, MagicMock())
        parent = getattr(parent, p)
