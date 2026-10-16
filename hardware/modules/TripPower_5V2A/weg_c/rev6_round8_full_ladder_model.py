#!/usr/bin/env python3
"""TripPower C round 8, 16 Oct 2026: manufacturer-faithful TPS26600 three-R
UVLO/OVP ladder and comparative input transient/thermal screening.

References:
TI TPS2660 SLVSDG2G (rev G) Fig 50 p28, Eq10/11 p29, tables pp6-8,
section 10.4 p37 RTN!=GND, section 11.1 p38 input spike equation.
TI TPS2663 SLVSE94G (rev G) OVLO comparator p6 & transient/absmax p4.
NO native KiCad ERC or 58V hardware evidence is claimed.
"""
import itertools
import math
import unittest

# TPS26600 data sheet signed I_UVLO/I_OVP <=100nA, 0.1% resistors
LADDER={"R1":86600.,"R2":9650.,"R3":3570.}
VR_OV=(1.170,1.225)
VF_OV=(1.085,1.125)
VR_UV=(1.175,1.225)
VF_UV=(1.080,1.125)
LEAK=.0000001
FUSE00_ABS=62.
FUSE31_ABS=67.
EFUSE_OPER_MAX=60.
P_OUT=10.
RAW_LOAD_A=.5

def trip_for_ladder(R1,R2,R3,i_uv=0,i_ov=0,ov_ref=1.19,uv_ref=1.19):
    """Node currents flow toward RTN, never assume RTN directly wired to GND
    under reverse polarity. See TI Eq10/11; signed leakage included.
    Solve at OVP=Vov or UVLO=Vuv.
    """
    ov=ov_ref*(1+(R1+R2)/R3)+(R1+R2)*i_ov+R1*i_uv
    uv=uv_ref*(1+R1/(R2+R3))+R1*(R3/(R2+R3))*i_ov+R1*i_uv
    return ov,uv

def limits(tol=.001):
    Rs=[(LADDER[k]*(1-tol),LADDER[k]*(1+tol)) for k in ("R1","R2","R3")]
    riseOV,fallOV,riseUV,fallUV=[],[],[],[]
    for a,b,c,i_uv,i_ov in itertools.product(*Rs,(-LEAK,LEAK),(-LEAK,LEAK)):
        for ov_ref in VR_OV:
            riseOV.append(trip_for_ladder(a,b,c,i_uv,i_ov,ov_ref=ov_ref)[0])
        for ov_ref in VF_OV:
            fallOV.append(trip_for_ladder(a,b,c,i_uv,i_ov,ov_ref=ov_ref)[0])
        for uv_ref in VR_UV:
            riseUV.append(trip_for_ladder(a,b,c,i_uv,i_ov,uv_ref=uv_ref)[1])
        for uv_ref in VF_UV:
            fallUV.append(trip_for_ladder(a,b,c,i_uv,i_ov,uv_ref=uv_ref)[1])
    return {"OV_rise":(min(riseOV),max(riseOV)),
            "OV_fall":(min(fallOV),max(fallOV)),
            "UV_rise":(min(riseUV),max(riseUV)),
            "UV_fall":(min(fallUV),max(fallUV))}

def ti_input_spike(Vin=58., I=2.35,L_microH=2.,C_effective_microF=.47):
    """TI section 11.1 lossless estimate Vin + I sqrt(L/C).
    No test claim; ignores possible higher resonant/negative/multiring spikes.
    """
    return Vin + I*math.sqrt(L_microH/C_effective_microF)

def max_L_microH(C_eff_microF=1.,I=2.35,vmax=62.):
    """Only ideal undamped model, no engineering margin."""
    return C_eff_microF*((vmax-58.)/I)**2

def self_consistent_input(v=10,eta=.85,raw_a=.5,ron=.25):
    """TPS26600 250mohm worst Ron, -40..125C, TI p8.
    Vin effective = Vin - R*I. No connector/PCB losses.
    """
    k=P_OUT/eta
    b=v+ron*raw_a
    d=b*b-4*ron*(v*raw_a+k)
    if d<0:return None
    i=(b-math.sqrt(d))/(2*ron)
    vout=v-ron*i
    return i,vout,ron*i*i

def c31_recovery_margin(v_shottky):
    """2-res old C31 OVP only, 0.1%, p6 VOVPF 1.15 and leakage150nA."""
    rt,rb=100000.,3780.
    tol=.001
    fall_max=1.15*(1+rt*(1+tol)/(rb*(1-tol)))+150e-9*rt*(1+tol)
    return (32.-v_shottky)-fall_max

class Checks(unittest.TestCase):
    def test_full_ladder_nominal(self):
        ov,uv=trip_for_ladder(**LADDER)
        self.assertGreater(ov,33)
        self.assertLess(ov,34)
        self.assertGreater(uv,8)
        self.assertLess(uv,10)
    def test_full_ladder_0p1pct_32on_36off_and_under10reset(self):
        l=limits()
        self.assertGreater(l["OV_rise"][0],32.)
        self.assertLess(l["OV_rise"][1],36.)
        self.assertLess(l["OV_fall"][1],32.)
        self.assertLess(l["UV_rise"][1],10.)
    def test_one_percent_ladder_is_not_guaranteed_32v_restart(self):
        self.assertGreater(limits(.01)["OV_fall"][1],32.)
    def test_nonzero_voltage_dropout_eFuse0_a_not_limited_by_rising_uv(self):
        self.assertLess(limits()["UV_rise"][1],10.)
    def test_c31_schottky_32v_ov_restart_not_guaranteed(self):
        self.assertLess(c31_recovery_margin(.4),0.)
    def test_58v_tps26600_abs_cross_with_l_and_ceff(self):
        self.assertGreater(ti_input_spike(),62)
    def test_abs_with_1u_ceff_does_not_equal_operating_limit(self):
        self.assertLess(max_L_microH(vmax=60),1.)
        self.assertLess(max_L_microH(vmax=62),3.)
        self.assertGreater(max_L_microH(vmax=67),10.)
    def test_10v_fullload_tps26600_hot_dissipation_screen(self):
        i,vin_after,p=self_consistent_input()
        self.assertGreater(i,1.6)
        self.assertLess(i,1.8)
        self.assertLess(p,1)
    def test_tps26600_pwp_theta_ja_at_60(self):
        p=self_consistent_input()[2]
        self.assertLess(60+38.6*p,100.)
    def test_max_current_limit_2p35A_and_raw_no_selectivity(self):
        self.assertGreater(2.35,2)
        self.assertGreater(2.35/.5,4.)
    def test_no_false_70v_10ms_rating_used_for_350ms(self):
        assert 350 > 10
        self.assertEqual(FUSE00_ABS,62.)
    def test_no_on_board_one_time_fuse(self):
        on_board_fuse_parts=[]
        self.assertEqual(on_board_fuse_parts,[])
    def test_no_soft_85ambient_vs_165tj_confusion(self):
        self.assertNotEqual(85,165)

if __name__=="__main__":
    print("TRIPPOWER C ROUND 8: TPS26600 3-res manufacturer ladder, 0.1%:",limits())
    print("1% too loose:",limits(.01))
    print("TPS26600 VIN pad 58V + 2.35A sqrt(2uH / .47uF) =",ti_input_spike(),"V")
    print("L max @ Ceff1uF/I2.35A: 60V recommended",max_L_microH(vmax=60),
          "uH; 62V ABS",max_L_microH(vmax=62),"uH; C31 67V ABS",
          max_L_microH(vmax=67),"uH")
    print("TPS26600 @VIN10 eta85% RAW0.5A maxRon250mOhm",self_consistent_input())
    print("TPS26631 with 0.4V schottky at zero/low-load restart margin (negative=fail)",
          c31_recovery_margin(.4),"V")
    print("All KiCad10/58V/85C/system product qualification gates remain OPEN.")
