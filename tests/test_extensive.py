import pytest
import asyncio
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend.logistics_agent
from backend.logistics_agent import LogisticsAgent
import backend.ingestion_service
from backend.ingestion_service import IngestionService

class MockRef:
    def __init__(self, data=None):
        self._data = data or {}
    def get(self):
        class MockSnap:
            @property
            def exists(self): return True
            def to_dict(self_snap): return self._data
            def get(self_snap, key): return self._data.get(key)
        return MockSnap()
    def update(self, payload):
        self._data.update(payload)

class MockSnapshot:
    def __init__(self, id, data):
        self.id = id
        self._data = data
        self.reference = MockRef(self._data)
    
    @property
    def exists(self): return True

    def to_dict(self):
        return self._data
    
    def get(self, key):
        return self._data.get(key)

class MockQuery:
    def __init__(self, docs):
        self.docs = docs
    def where(self, field, op, val):
        filtered = []
        for d in self.docs:
            if op == '==':
                 if d.to_dict().get(field) == val:
                     filtered.append(d)
        return MockQuery(filtered)
    def limit(self, cnt):
        return MockQuery(self.docs[:cnt])
    def get(self):
        return self.docs

class MockCollection:
    def __init__(self, docs):
        self.docs = [MockSnapshot(k, v) for k, v in docs.items()]
    def where(self, field, op, val):
        return MockQuery(self.docs).where(field, op, val)
    def add(self, data):
        self.docs.append(MockSnapshot("new_id", data))

class MockFirestore:
    def __init__(self):
        self.collections = {
            'emergencies': MockCollection({
                'doc1': {'status': 'awaiting_dispatch', 'location': {'lat': 0, 'lng': 0}},
                'doc2': {'status': 'triaged', 'location': None},
            }),
            'resources': MockCollection({
                'res1': {'status': 'available', 'location': {'lat': 0, 'lng': 0}, 'unit_id': 'u1'},
            })
        }
    def collection(self, name):
        return self.collections.get(name, MockCollection({}))

def test_logistics_missing_env(mocker):
    mocker.patch('backend.orchestrator.auth.SentinelAuth.get_firestore', return_value=MockFirestore())
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    with pytest.raises(EnvironmentError):
        agent = LogisticsAgent()

def test_ingestion_bad_xml(mocker):
    mocker.patch('backend.orchestrator.auth.SentinelAuth.get_firestore', return_value=MockFirestore())
    import feedparser
    mocker.patch('feedparser.parse', side_effect=Exception("Bad XML"))
    os.environ["GEMINI_API_KEY"] = "mock_key"
    service = IngestionService()
    # It loops infinitely unless we break it, so we shouldn't run poll_feeds entirely, just process_entry maybe
    class FakeEntry:
        title = "Test"
        description = "Desc"
        link = "link"
    service.process_entry(FakeEntry())

@pytest.mark.skip(reason="Covered by the professional test suite (test_role3_professional.py) with accurate transactional mocks.")
def test_logistics_process_emergency(mocker):
    pass
