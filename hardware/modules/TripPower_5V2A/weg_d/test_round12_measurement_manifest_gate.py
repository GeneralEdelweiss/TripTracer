import unittest

from round12_measurement_manifest_gate import plan_integrity, assess_capture


class Round12CaptureGate(unittest.TestCase):
    @staticmethod
    def capture(*points):
        return {"stage": "BENCH_A23", "run_id": "SYNTHETIC_TEST_NOT_HARDWARE",
                "equipment_ids": ["FAKE_TEST_SCOPE"],
                "measurements":list(points)}

    @staticmethod
    def p(point_id="P09", mn=32.0, mx=59.0, uncertainty=0.5):
        return {"point_id":point_id, "min_v":mn,"max_v":mx,
                "expanded_uncertainty_v":uncertainty,
                "raw_waveform_path":"NOT_A_REAL_TRACE_synthetic.wfm",
                "probe_id":"FAKE_SCOPE_SYNTHETIC"}

    def test_matrix_checks_m8_and_q202(self):
        result=plan_integrity()
        self.assertEqual(result["point_count"],40)
        self.assertEqual(result["status"],"PLAN_INTEGRITY_ONLY")
        self.assertEqual(result["hardware_measurements"],"NOT_RUN")

    def test_in_sys_within_requested_operating_limit_is_not_hardware_pass(self):
        x=assess_capture(self.capture(self.p()))
        self.assertEqual(x["results"][0]["numeric_status"],"NUMERIC_WITHIN_RECOMMENDED_ONLY")
        self.assertEqual(x["status"],"ENGINEER_REVIEW_REQUIRED_NOT_HARDWARE_PASS")
        self.assertGreater(len(x["missing_required_points"]),0)

    def test_60v_recommended_limit_is_an_engineering_gate(self):
        x=assess_capture(self.capture(self.p(mx=59.9,uncertainty=0.2)))
        self.assertEqual(x["results"][0]["numeric_status"],"RECOMMENDED_LIMIT_REVIEW_OR_FAIL")

    def test_67v_absolute_limit_is_stop(self):
        x=assess_capture(self.capture(self.p(mx=66.9,uncertainty=0.2)))
        self.assertEqual(x["results"][0]["numeric_status"],"ABSOLUTE_LIMIT_STOP")

    def test_q202_drainsource_50v_absolute(self):
        x=assess_capture(self.capture(self.p(point_id="P14",mn=0,mx=50.1,uncertainty=.1)))
        self.assertEqual(x["results"][0]["numeric_status"],"ABSOLUTE_LIMIT_STOP")

    def test_missing_waveform_is_rejected(self):
        p=self.p(); p["raw_waveform_path"]=""
        with self.assertRaises(ValueError):
            assess_capture(self.capture(p))

    def test_m8_cannot_be_renamed_module_input(self):
        with self.assertRaises(ValueError):
            assess_capture(self.capture(self.p(point_id="P02")))

    def test_no_dynamically_invented_ti_spice_result(self):
        self.assertEqual(plan_integrity()["vendor_pspice"],"NOT_RUN")


if __name__=="__main__":
    unittest.main()
