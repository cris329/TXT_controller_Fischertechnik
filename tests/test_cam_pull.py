# -*- coding: utf-8 -*-
"""CamPuller buffer local.

@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pc.cam_pull import CamPuller


def test_not_live_initially():
    """Sin snaps, is_live False."""
    pull = CamPuller("127.0.0.1")
    assert pull.get_jpeg() is None
    assert pull.is_live() is False


def test_live_after_stamp():
    """Con last_ok reciente, is_live True."""
    pull = CamPuller("127.0.0.1")
    pull.last_ok = time.time()
    pull.latest = b"\xff\xd8xx"
    assert pull.is_live() is True
    assert pull.get_jpeg() == b"\xff\xd8xx"
