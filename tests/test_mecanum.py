# -*- coding: utf-8 -*-
"""Unit tests for mecanum kinematics.

@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.mecanum import mecanum_speeds
from shared.protocol import clamp


def test_forward_all_same_sign():
    """Happy path: forward yields same-sign wheel speeds."""
    m1, m2, m3, m4 = mecanum_speeds(1, 0, 0, 512)
    assert m1 > 0 and m2 > 0 and m3 > 0 and m4 > 0


def test_stop_zero():
    """Edge: zero axes produce zero PWM."""
    assert mecanum_speeds(0, 0, 0) == (0, 0, 0, 0)


def test_clamp_error_bounds():
    """Error/edge: clamp rejects out-of-range values."""
    assert clamp(2, -1, 1) == 1
    assert clamp(-9, -1, 1) == -1


def test_rotate_opposite_sides():
    """Happy path: pure rotation differs left/right."""
    m1, m2, m3, m4 = mecanum_speeds(0, 0, 1, 512)
    assert m1 < 0 and m2 > 0
