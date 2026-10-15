import unittest
from cots_b_compare import compare

class QuotedCoreSubset(unittest.TestCase):
    def test_priced_subset_has_three_quantity_breaks(self):
        rows=compare()["priced_IC_subset"]
        self.assertEqual([r["qty"] for r in rows],[1,10,100])
        self.assertAlmostEqual(rows[0]["LM74930_plus_LMR38020_eur"],8.33)
        self.assertAlmostEqual(rows[0]["LTC4380_delta_eur"],4.65)
        self.assertAlmostEqual(rows[1]["LTC4380_delta_eur"],3.731)
        self.assertAlmostEqual(rows[2]["LTC4380_delta_eur"],3.2325)
    def test_not_inventing_system_price_or_new_placement_count(self):
        d=compare()
        self.assertEqual((d["entire_module_fit_AUTO"],d["entire_module_fit_RUN"]),(57,58))
        self.assertIsNone(d["full_new_architecture_cost_EUR"])
        self.assertIsNone(d["full_new_architecture_BOM_placement_count"])
    def test_cost_delta_not_free_safety(self):
        d=compare()
        self.assertTrue(d["B_extra_HV_FET_SOA_and_VCC_clamp_required"])
        self.assertTrue(all(row["LTC4380_delta_eur"]>0 for row in d["priced_IC_subset"]))
if __name__=="__main__": unittest.main()
