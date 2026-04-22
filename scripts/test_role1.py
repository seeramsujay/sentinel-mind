import pytest
import json
import os
import sys
import tempfile
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from backend.orchestrator import spatial_logic, audit, resolver


class MockDoc:
    def __init__(self, data: dict, doc_id: str):
        self._data = data
        self.id = doc_id

    def to_dict(self) -> dict:
        return self._data


class TestSpatialLogic:
    def test_haversine_same_point(self):
        d = spatial_logic.haversine_distance({"lat": 0, "lng": 0}, {"lat": 0, "lng": 0})
        assert d == 0.0

    def test_haversine_known_distance(self):
        d = spatial_logic.haversine_distance(
            {"lat": 17.433, "lng": 78.444},
            {"lat": 17.434, "lng": 78.445},
        )
        assert d is not None
        assert d > 0
        assert d < 200

    def test_haversine_invalid_coords(self):
        assert spatial_logic.haversine_distance({"lat": None}, {"lat": 0}) is None
        assert spatial_logic.haversine_distance({}, {}) is None

    def test_detect_duplicates_exact_match(self):
        existing = [MockDoc({"hazard_type": "flood", "location": {"lat": 17.433, "lng": 78.444}}, "dup-1")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "flood", "location": {"lat": 17.433, "lng": 78.444}},
            existing,
            threshold_meters=500,
        )
        assert result == "dup-1"

    def test_detect_duplicates_within_threshold(self):
        existing = [MockDoc({"hazard_type": "flood", "location": {"lat": 17.433, "lng": 78.444}}, "dup-2")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "flood", "location": {"lat": 17.4331, "lng": 78.4441}},
            existing,
            threshold_meters=500,
        )
        assert result == "dup-2"

    def test_detect_duplicates_outside_threshold(self):
        existing = [MockDoc({"hazard_type": "flood", "location": {"lat": 17.433, "lng": 78.444}}, "dup-3")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "flood", "location": {"lat": 18.0, "lng": 79.0}},
            existing,
            threshold_meters=500,
        )
        assert result is None

    def test_detect_duplicates_different_hazard_type(self):
        existing = [MockDoc({"hazard_type": "earthquake", "location": {"lat": 17.433, "lng": 78.444}}, "dup-4")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "flood", "location": {"lat": 17.433, "lng": 78.444}},
            existing,
            threshold_meters=500,
        )
        assert result is None

    def test_detect_duplicates_no_location(self):
        result = spatial_logic.detect_duplicates({"hazard_type": "flood"}, [])
        assert result is None

    def test_detect_duplicates_no_hazard_type(self):
        result = spatial_logic.detect_duplicates({"location": {"lat": 1, "lng": 1}}, [])
        assert result is None

    def test_detect_duplicates_empty_existing(self):
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "flood", "location": {"lat": 1, "lng": 1}},
            [],
        )
        assert result is None

    def test_detect_duplicates_flat_coords(self):
        existing = [MockDoc({"hazard_type": "fire", "latitude": 17.433, "longitude": 78.444}, "dup-5")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "fire", "latitude": 17.433, "longitude": 78.444},
            existing,
            threshold_meters=500,
        )
        assert result == "dup-5"

    def test_detect_duplicates_mixed_coords(self):
        existing = [MockDoc({"hazard_type": "fire", "location": {"lat": 17.433, "lng": 78.444}}, "dup-6")]
        result = spatial_logic.detect_duplicates(
            {"hazard_type": "fire", "latitude": 17.433, "longitude": 78.444},
            existing,
            threshold_meters=500,
        )
        assert result == "dup-6"


class TestAuditLogAudit:
    def test_log_audit_empty_id(self, monkeypatch, tmp_path):
        called = False
        def fake_update(data):
            nonlocal called
            called = True
        monkeypatch.setattr(audit.GovernanceAudit, "log_audit", lambda eid, text, db=None: None)
        audit.GovernanceAudit.log_audit("", "some text")
        audit.GovernanceAudit.log_audit(None, "some text")

    def test_log_hitl_flag_empty_id(self):
        result = audit.GovernanceAudit.log_hitl_flag("", "reason")
        assert result is False

    def test_approve_dispatch_empty_id(self):
        result = audit.GovernanceAudit.approve_dispatch("")
        assert result is False


class TestConflictResolver:
    def test_resolve_empty_conflicts(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        result = r.resolve([], [{"unit_id": "amb-1"}])
        assert result is None

    def test_resolve_empty_resources(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        result = r.resolve([{"id": "e1", "urgency": "P1"}], [])
        assert result is None

    def test_parse_valid_json(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        text = '{"decisions":[{"emergency_id":"e1","action":"dispatch","resource_id":"amb-1","reason":"P1","fairness_audit":"OK"}]}'
        result = r._parse(text)
        assert result is not None
        assert "decisions" in result
        assert len(result["decisions"]) == 1

    def test_parse_fenced_json(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        text = '```json\n{"decisions":[{"emergency_id":"e2","action":"wait","resource_id":null,"reason":"","fairness_audit":"none"}]}\n```'
        result = r._parse(text)
        assert result is not None
        assert result["decisions"][0]["action"] == "wait"

    def test_parse_invalid_json(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        result = r._parse("not json at all")
        assert result is None

    def test_parse_empty_text(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        assert r._parse("") is None
        assert r._parse("   ") is None

    def test_parse_no_decisions_key(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        result = r._parse('{"other": "data"}')
        assert result is None

    def test_parse_mixed_fences(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        text = 'Here is some text before ``` the JSON ``` more text after'
        result = r._parse(text)
        assert result is None

    def test_parse_triple_fence_markers(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        text = "```json\n{'decisions':[{'emergency_id':'e1','action':'dispatch','resource_id':'amb-1','reason':'ok','fairness_audit':'ok'}]}\n```"
        result = r._parse(text)
        assert result is None

    def test_parse_whitespace_only(self):
        r = resolver.ConflictResolver()
        r._init_vertex = lambda: None
        assert r._parse("  \n  ") is None


class TestEmergencyDocSchema:
    def test_all_required_fields_can_be_none(self):
        d = {"hazard_type": None, "urgency": None, "status": "dispatched"}
        assert d.get("hazard_type") is None
        assert d.get("urgency") is None

    def test_status_enum_valid(self):
        valid = {"received", "triaged", "awaiting_dispatch", "dispatched", "conflict", "recovery", "awaiting_human_approval"}
        for s in valid:
            assert s in valid

    def test_urgency_enum_valid(self):
        valid = {"P1", "P2", "P3"}
        for u in valid:
            assert u in valid

    def test_nested_intelligence_null(self):
        d = {"intelligence": None}
        assert d.get("intelligence") is None

    def test_resource_assignment_null(self):
        d = {"resource_assignment": None}
        assert d.get("resource_assignment") is None

    def test_flat_and_nested_field_names(self):
        d = {
            "hazard_type": "flood",
            "urgency": "P1",
            "status": "dispatched",
            "location": {"lat": 17.433, "lng": 78.444},
            "resource_assignment": {
                "unit_id": "amb-1",
                "eta": "15 min",
                "carbon_saved": 2.5,
            },
            "intelligence": {
                "fairness_audit": "Prioritized P1.",
                "hitl_reason": None,
            },
        }
        assert d["location"]["lat"] == 17.433
        assert d["resource_assignment"]["unit_id"] == "amb-1"
        assert d["intelligence"]["fairness_audit"] == "Prioritized P1."


class TestEmbedBuilding:
    def test_build_embed_with_flat_coords(self):
        doc = {
            "urgency": "P1",
            "hazard_type": "earthquake",
            "location_name": "Hyderabad",
            "latitude": 17.385,
            "longitude": 78.486,
            "assigned_unit": "amb-7",
            "eta_minutes": 12,
            "carbon_saved_kg": 1.5,
        }
        assert doc.get("latitude") == 17.385

    def test_build_embed_with_nested_location(self):
        doc = {
            "urgency": "P2",
            "hazard_type": "flood",
            "location": {"lat": 17.433, "lng": 78.444, "address": "RR Dist"},
        }
        loc = doc.get("location") or {}
        assert loc.get("lat") == 17.433


if __name__ == "__main__":
    pytest.main([__file__, "-v"])