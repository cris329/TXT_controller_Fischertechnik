# -*- coding: utf-8 -*-
"""Unit tests for Xbox deadzone helper.

@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pc.xbox_input import DEADZONE, _dz


def test_deadzone_filters_noise():
    """Happy path: small stick noise becomes zero."""
    assert _dz(DEADZONE / 2) == 0.0


def test_deadzone_keeps_real_input():
    """Edge: values above deadzone pass through."""
    assert _dz(0.9) == 0.9


def test_deadzone_clamps():
    """Error: huge values clamp to [-1, 1]."""
    assert _dz(5) == 1.0
    assert _dz(-5) == -1.0
