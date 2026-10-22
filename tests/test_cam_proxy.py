# -*- coding: utf-8 -*-
"""Helpers de proxy de camara.

@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import os
import sys
from unittest.mock import MagicMock, patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pc.cam_proxy import snap_ok


def test_snap_ok_true():
    """snap_ok True cuando hay JPEG."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"\xff\xd8" + b"x" * 40
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    with patch("pc.cam_proxy.urllib.request.urlopen", return_value=mock_resp):
        assert snap_ok("1.2.3.4") is True


def test_snap_ok_false_on_error():
    """snap_ok False si falla la red."""
    with patch(
        "pc.cam_proxy.urllib.request.urlopen", side_effect=OSError("down")
    ):
        assert snap_ok("1.2.3.4") is False
