import unittest
import math
import os
import json

from telemetry_sim import StadiumTelemetryEngine
from ml_engine import StadiumMLEngine
from ric_controller import ORANNearRTRICController

class TestAirtelSyncPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.telemetry = StadiumTelemetryEngine()
        cls.ml = StadiumMLEngine()
        cls.ric = ORANNearRTRICController()

    def test_01_data_ingestion(self):
        self.assertIsNotNone(self.telemetry.ground_truth)
        self.assertIn("telemetry", self.telemetry.ground_truth)
        self.assertIn("sites", self.telemetry.ground_truth)
        self.assertIn("upi", self.telemetry.ground_truth)
        self.assertEqual(len(self.telemetry.existing_sites), 8)
        self.assertEqual(len(self.telemetry.proposed_sites), 18)

    def test_02_dimensioning_100k(self):
        dim = self.telemetry.calculate_dimensioning(100000)
        self.assertEqual(dim["airtel_subscribers"], 40000)
        self.assertEqual(dim["peak_active_users"], 7200)
        self.assertEqual(dim["users_5g"], 5040)
        self.assertEqual(dim["users_4g"], 2160)
        self.assertEqual(dim["demand_5g_mbps"], 25200.0)
        self.assertEqual(dim["demand_4g_mbps"], 6480.0)
        self.assertEqual(dim["total_demand_mbps"], 31680.0)

        self.assertEqual(dim["usable_cap_5g_mbps"], 2100.0)
        self.assertEqual(dim["usable_cap_4g_mbps"], 308.0)
        self.assertEqual(dim["req_cells_5g"], 12)
        self.assertEqual(dim["req_cells_4g"], 22)
        self.assertEqual(dim["extra_5g_needed"], 8)
        self.assertEqual(dim["extra_4g_needed"], 14)

    def test_03_capex_budget(self):
        sim = self.telemetry.simulate_stadium(100000, "21:00", toggle_capex=True, toggle_signaling=True, toggle_qos=True)
        self.assertEqual(sim["capex_spent_lakhs"], 387.0)
        self.assertEqual(sim["budget_remaining_lakhs"], 13.0)
        self.assertLessEqual(sim["capex_spent_lakhs"], 400.0)

    def test_04_forensic_calibration_65k(self):
        sim_65k = self.telemetry.simulate_stadium(65000, "21:00", toggle_capex=False, toggle_signaling=False, toggle_qos=False)
        self.assertAlmostEqual(sim_65k["5g_success_rate_pct"], 35.8, delta=1.5)
        self.assertAlmostEqual(sim_65k["avg_4g_speed_mbps"], 1.0, delta=0.2)
        self.assertAlmostEqual(sim_65k["upi_failure_rate_pct"], 7.11, delta=0.5)
        self.assertGreaterEqual(sim_65k["avg_prb_load_pct"], 95.0)

    def test_05_solution_slas_100k(self):
        sim_sync = self.telemetry.simulate_stadium(100000, "21:00", toggle_capex=True, toggle_signaling=True, toggle_qos=True)

        self.assertGreaterEqual(sim_sync["avg_5g_speed_mbps"], 5.0)

        self.assertGreaterEqual(sim_sync["avg_4g_speed_mbps"], 3.0)

        self.assertGreaterEqual(sim_sync["5g_success_rate_pct"], 95.0)

        self.assertLessEqual(sim_sync["upi_failure_rate_pct"], 1.0)

        self.assertLessEqual(sim_sync["avg_prb_load_pct"], 80.0)

    def test_06_ml_dbscan_clustering(self):
        coords = self.ml.generate_user_coordinates(1000, "21:00")
        self.assertEqual(len(coords), 1000)
        coords, hotspots = self.ml.cluster_hotspots_dbscan(coords, eps=30.0, min_samples=15)
        self.assertGreater(len(hotspots), 0)

        for h in hotspots:
            self.assertIn(h["recommended_downtilt_deg"], [8.0, 15.0, 30.0])

    def test_07_temporal_surge_forecaster(self):
        fc_2100 = self.ml.forecast_surge_15min_ahead("21:00")
        self.assertIn("CRITICAL", fc_2100["concourse_surge_risk"])
        fc_2245 = self.ml.forecast_surge_15min_ahead("22:45")
        self.assertIn("6:4", fc_2245["ric_action"])

    def test_08_oran_ric_and_emergency(self):
        status = self.ric.configure_xapps(toggle_capex=True, toggle_signaling=True, toggle_qos=True)
        self.assertGreater(len(status), 0)
        trace = self.ric.simulate_emergency_call()
        self.assertEqual(len(trace), 6)

        self.assertIn("pre-empts", trace[4]["action"].lower())

if __name__ == "__main__":
    unittest.main()
