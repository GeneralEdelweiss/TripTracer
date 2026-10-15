#!/usr/bin/env python3
"""Mutation regression: the native-path validator must reject reversed TVS pins."""
import unittest
from check_trippower_a_netlist import EXPECTED, verify

SYMBOL_TEXT = (
    "Cathode pad1, anode pad2 "
    + " ".join(f'(property "Reference" "{r}") (property "MPN" "{m}")'
      for r,m in (("Q301","SQM10250E_GE3"),("D301","1SMB5943BT3G"),
                  ("D302","BAV21WQ-7-F"),("D303","SMBJ150A-13-F"),
                  ("D304","SMBJ33CA-13-F")))
    + " ".join(f'(property "Reference" "{r}")' for r in ("R313","R314","R315"))
    + ' (property "MPN" "CRCW25123K30FKEGHP")'*3
)

def synthetic_nets():
    data={}
    for ref,pins in EXPECTED.items():
        for pin,name in pins.items():
            data.setdefault(name,set()).add((ref,pin))
    return data

class PolarityMutationTests(unittest.TestCase):
    def test_correct_native_pin_map_accepted_synthetically(self):
        self.assertTrue(verify(synthetic_nets(),SYMBOL_TEXT)
                        ["native_netlist_topology_pass"])

    def test_reversed_d303_150v_tvs_fails(self):
        data=synthetic_nets()
        data["VIN_FUSED"].remove(("D303","1"))
        data["TVS_STACK"].remove(("D303","2"))
        data["VIN_FUSED"].add(("D303","2"))
        data["TVS_STACK"].add(("D303","1"))
        with self.assertRaises(AssertionError):
            verify(data,SYMBOL_TEXT)

    def test_bypassed_vs_series_midpoint_fails(self):
        data=synthetic_nets()
        data["VS_SERIES_A"].remove(("R314","1"))
        data["VIN_FUSED"].add(("R314","1"))
        with self.assertRaises(AssertionError):
            verify(data,SYMBOL_TEXT)

if __name__=="__main__": unittest.main()
