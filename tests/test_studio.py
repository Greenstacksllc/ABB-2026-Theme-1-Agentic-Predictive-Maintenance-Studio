import unittest

from studio import MaintenanceStudio, demo_rows


class StudioTests(unittest.TestCase):
    def test_escalation_reuses_one_draft_and_requires_review(self):
        studio = MaintenanceStudio()
        results = [studio.ingest(row) for row in demo_rows()]
        self.assertEqual([r["severity"] for r in results],
                         ["normal", "normal", "warning", "critical", "normal"])
        self.assertEqual(len(studio.work_orders), 1)
        order = studio.work_orders["WO-PUMP-02"]
        self.assertEqual(order["status"], "needs_review")
        self.assertEqual(len(order["evidence"]), 2)
        with self.assertRaises(ValueError):
            studio.review(order["id"], "approve", "")
        self.assertEqual(studio.review(order["id"], "approve", "Technician A")["status"], "approved")
        with self.assertRaises(ValueError):
            studio.review(order["id"], "dismiss", "Technician B")

    def test_invalid_and_out_of_order_observations_do_not_change_state(self):
        studio = MaintenanceStudio()
        first = demo_rows()[0]
        self.assertTrue(studio.ingest(first)["accepted"])
        for bad in (first, {**first, "timestamp": "2026-09-24T11:59:59Z"},
                    {**first, "timestamp": "2026-09-24T12:00:05Z", "temperature_c": "nan"},
                    {**first, "timestamp": "2026-09-24T12:00:05Z", "pressure_bar": -1},
                    {**first, "timestamp": "2026-09-24T12:00:05"}):
            self.assertFalse(studio.ingest(bad)["accepted"])
        self.assertEqual(studio.assets["MOTOR-01"].observations, 1)
        self.assertEqual(len(studio.events), 1)
        self.assertEqual(len(studio.rejections), 5)

    def test_isolated_asset_streaks(self):
        studio = MaintenanceStudio()
        rows = demo_rows()
        studio.ingest(rows[2])
        studio.ingest(rows[0])
        self.assertEqual(studio.assets["PUMP-02"].elevated_streak, 1)
        self.assertEqual(studio.assets["MOTOR-01"].elevated_streak, 0)


if __name__ == "__main__":
    unittest.main()
