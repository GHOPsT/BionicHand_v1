import unittest
import numpy as np
from core.hand import BionicHand

class TestBionicHandKinematics(unittest.TestCase):
    def setUp(self):
        self.hand = BionicHand()

    def test_finger_link_lengths(self):
        """Verifica que las distancias calculadas correspondan al CAD."""
        for f in self.hand.fingers:
            pts = f.get_positions()
            l1_calc = np.linalg.norm(pts - pts[0])
            self.assertAlmostEqual(l1_calc, f.l1, delta=1e-5)
            l2_calc = np.linalg.norm(pts - pts)
            self.assertAlmostEqual(l2_calc, f.l2, delta=1e-5)

    def test_joint_limits_clamping(self):
        """Comprueba que ninguna articulación exceda los topes mecánicos físicos."""
        self.hand.set_actuators(u_index=2.0, u_group=2.0, u_thumb=2.0)
        for f in self.hand.fingers:
            self.assertLessEqual(f.mcp.angle, f.mcp.max_deg + 1e-5)
            self.assertLessEqual(f.pip.angle, f.pip.max_deg + 1e-5)

    def test_subactuated_group_synchronization(self):
        """Verifica la flexión sincronizada de medio, anular y meñique."""
        self.hand.set_actuators(u_index=0.0, u_group=0.5, u_thumb=0.0)
        self.assertAlmostEqual(self.hand.index.mcp.normalized, 0.0)
        self.assertAlmostEqual(self.hand.middle.mcp.normalized, 0.5)
        self.assertAlmostEqual(self.hand.ring.mcp.normalized, 0.5)
        self.assertAlmostEqual(self.hand.pinky.mcp.normalized, 0.5)

if __name__ == "__main__":
    unittest.main()