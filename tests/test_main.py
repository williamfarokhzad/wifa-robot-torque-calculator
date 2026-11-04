import math
import random
import unittest
from main import calculate


class TorqueTests(unittest.TestCase):
    def test_single_link_known_lever(self):
        r=calculate([0.4],[2],[0],payload_kg=1)
        self.assertAlmostEqual(r['holding_torque_Nm'][0],9.81*(2*0.2+1*0.4))

    def test_two_link_horizontal_reference(self):
        r=calculate([0.3,0.2],[1,0.5],[0,0],payload_kg=0.4)
        self.assertAlmostEqual(r['holding_torque_Nm'][0],5.3955)
        self.assertAlmostEqual(r['holding_torque_Nm'][1],1.2753)

    def test_folded_elbow_reverses_sign(self):
        r=calculate([0.3,0.2],[1,0.5],[0,math.pi],payload_kg=0.4)
        self.assertAlmostEqual(r['holding_torque_Nm'][0],2.8449)
        self.assertAlmostEqual(r['holding_torque_Nm'][1],-1.2753)

    def test_vertical_gravity_moment_is_zero(self):
        r=calculate([0.3,0.2],[1,0.5],[math.pi/2,0],payload_kg=0.4)
        for value in r['holding_torque_Nm']: self.assertLess(abs(value),1e-12)

    def test_zero_mass_zero_torque(self):
        self.assertEqual(calculate([0.3,0.2],[0,0],[0.4,0.2])['holding_torque_Nm'],[0,0])

    def test_payload_delta_matches_lever(self):
        a=calculate([0.3,0.2],[1,0.5],[0,0])
        b=calculate([0.3,0.2],[1,0.5],[0,0],payload_kg=0.4)
        self.assertAlmostEqual(b['holding_torque_Nm'][0]-a['holding_torque_Nm'][0],0.4*9.81*0.5)

    def test_left_pose_reverses_shoulder(self):
        self.assertAlmostEqual(calculate([0.4],[2],[math.pi])['holding_torque_Nm'][0],-3.924)

    def test_com_at_joint_has_no_own_lever(self):
        self.assertEqual(calculate([0.4],[2],[0],com_fractions=[0])['holding_torque_Nm'],[0])

    def test_potential_energy_gradient_independent_check(self):
        rng=random.Random(2026)
        for _ in range(20):
            angles=[rng.uniform(-math.pi,math.pi) for i in range(3)]
            kwargs={'lengths_m':[0.3,0.2,0.1],'masses_kg':[1,0.5,0.2],'payload_kg':0.4}
            torque=calculate(angles_rad=angles,**kwargs)['holding_torque_Nm']
            for joint in range(3):
                plus,minus=angles.copy(),angles.copy()
                plus[joint]+=1e-6;minus[joint]-=1e-6
                derivative=(calculate(angles_rad=plus,**kwargs)['potential_energy_J']-calculate(angles_rad=minus,**kwargs)['potential_energy_J'])/2e-6
                self.assertAlmostEqual(torque[joint],derivative,delta=1e-7)

    def test_invalid_data(self):
        cases=[([],[],[]),([0],[1],[0]),([1],[-1],[0]),([1],[1],[math.nan]),([True],[1],[0]),([1,2],[1],[0])]
        for args in cases:
            with self.subTest(args=args),self.assertRaises(ValueError):calculate(*args)
        for kwargs in ({'com_fractions':[1.1]},{'payload_kg':-1},{'gravity':math.inf}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):calculate([1],[1],[0],**kwargs)


if __name__ == '__main__':
    unittest.main()
