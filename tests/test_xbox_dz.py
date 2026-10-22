# -*- coding: utf-8 -*-
"""Deadzone del mando.

@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pc.xbox_input import _dz


def test_deadzone_zero():
    """Valores pequenos se anulan."""
    assert _dz(0.1) == 0.0
    assert _dz(-0.05) == 0.0


def test_deadzone_pass():
    """Fuera de zona se conserva (clamp)."""
    assert _dz(0.5) == 0.5
    assert _dz(-1.2) == -1.0


def test_turn_scales_exist():
    """Constantes de giro atenuado definidas."""
    from pc.xbox_input import TURN_SCALE, TURN_SCALE_MOVING

    assert 0 < TURN_SCALE_MOVING < TURN_SCALE <= 1.0
