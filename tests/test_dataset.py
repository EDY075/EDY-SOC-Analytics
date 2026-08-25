import csv
import hashlib
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generator.generate_dataset import generate  # noqa: E402


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = generate()

    def test_minimum_history_and_counts(self):
        start = datetime.fromisoformat(self.manifest["periodStart"])
        end = datetime.fromisoformat(self.manifest["periodEnd"])
        self.assertGreaterEqual((end - start).days, 365)
        self.assertEqual(self.manifest["counts"]["expected/FactSecurityEvents.csv"], 120000)
        self.assertEqual(self.manifest["counts"]["expected/FactAlerts.csv"], 18000)
        self.assertEqual(self.manifest["counts"]["expected/FactIncidents.csv"], 3200)

    def test_seed_is_deterministic(self):
        before = dict(self.manifest["sha256"])
        after = generate()["sha256"]
        self.assertEqual(before, after)

    def test_raw_duplicates_are_controlled_and_expected_is_unique(self):
        raw = rows(ROOT / "data" / "raw" / "security_events_raw.csv")
        expected = rows(ROOT / "data" / "expected" / "FactSecurityEvents.csv")
        raw_ids = [r["event_id"] for r in raw]
        expected_ids = [r["EventId"] for r in expected]
        self.assertEqual(len(raw_ids) - len(set(raw_ids)), 720)
        self.assertEqual(len(expected_ids), len(set(expected_ids)))

    def test_nulls_are_injected_only_in_raw_layer(self):
        raw_events = rows(ROOT / "data" / "raw" / "security_events_raw.csv")
        expected_events = rows(ROOT / "data" / "expected" / "FactSecurityEvents.csv")
        self.assertGreater(sum(not r["asset_id"] for r in raw_events), 0)
        missing_event_ids = {r["event_id"] for r in raw_events if not r["asset_id"]}
        unknown_member_ids = {r["EventId"] for r in expected_events if r["AssetKey"] == "0"}
        self.assertEqual(unknown_member_ids, missing_event_ids)

    def test_referential_integrity(self):
        assets = {r["AssetKey"] for r in rows(ROOT / "data" / "reference" / "DimAsset.csv")}
        rules = {r["DetectionRuleKey"] for r in rows(ROOT / "data" / "reference" / "DimDetectionRule.csv")}
        severities = {r["SeverityKey"] for r in rows(ROOT / "data" / "reference" / "DimSeverity.csv")}
        for table in ("FactSecurityEvents.csv", "FactAlerts.csv", "FactIncidents.csv"):
            fact = rows(ROOT / "data" / "expected" / table)
            self.assertTrue(all(r["AssetKey"] in assets for r in fact))
            self.assertTrue(all(r["DetectionRuleKey"] in rules for r in fact))
            self.assertTrue(all(r["SeverityKey"] in severities for r in fact))

    def test_missing_analyst_uses_unknown_member(self):
        raw_incidents = rows(ROOT / "data" / "raw" / "incidents_raw.csv")
        expected_incidents = rows(ROOT / "data" / "expected" / "FactIncidents.csv")
        missing_ids = {r["incident_id"] for r in raw_incidents if not r["analyst_id"]}
        unknown_ids = {r["IncidentId"] for r in expected_incidents if r["AnalystKey"] == "0"}
        self.assertEqual(unknown_ids, missing_ids)

    def test_incident_lifecycle_sequence(self):
        order_by_incident = {}
        for row in rows(ROOT / "data" / "expected" / "FactIncidentLifecycle.csv"):
            order_by_incident.setdefault(row["IncidentKey"], []).append((int(row["StageOrder"]), datetime.fromisoformat(row["StageAtUTC"].replace("Z", "+00:00"))))
        for stages in order_by_incident.values():
            stages.sort()
            self.assertEqual([o for o, _ in stages], sorted(o for o, _ in stages))
            self.assertEqual([d for _, d in stages], sorted(d for _, d in stages))

    def test_sla_logic(self):
        for row in rows(ROOT / "data" / "expected" / "FactSLA.csv"):
            if row["AcknowledgeActualMinutes"]:
                expected = float(row["AcknowledgeActualMinutes"]) <= float(row["AcknowledgeTargetMinutes"])
                self.assertEqual(row["AcknowledgeMet"] == "True", expected)
            if row["OverallMet"] == "True":
                self.assertEqual(row["AcknowledgeMet"], "True")
                self.assertEqual(row["ContainMet"], "True")
                self.assertEqual(row["ResolveMet"], "True")

    def test_mitre_keys_are_valid(self):
        techniques = {r["AttackTechniqueKey"] for r in rows(ROOT / "data" / "reference" / "DimAttackTechnique.csv")}
        bridge = rows(ROOT / "data" / "expected" / "BridgeIncidentTechnique.csv")
        self.assertTrue(all(r["AttackTechniqueKey"] in techniques for r in bridge))
        self.assertEqual(len({r["IncidentTechniqueKey"] for r in bridge}), len(bridge))

    def test_manifest_hashes_match_files(self):
        for relative, expected_hash in self.manifest["sha256"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected_hash, relative)

    def test_expected_kpis_are_sane(self):
        kpis = json.loads((ROOT / "data" / "expected" / "kpi_expected.json").read_text(encoding="utf-8"))
        self.assertEqual(kpis["Total Events"], 120000)
        self.assertEqual(kpis["Total Incidents"], 3200)
        self.assertGreater(kpis["MTTD Minutes"], 0)
        self.assertTrue(0 <= kpis["SLA Compliance"] <= 1)


if __name__ == "__main__":
    unittest.main()
