# -*- coding: utf-8 -*-
"""Defaults CameraPublisher (HTTP-first, MQTT off).

@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from robot.camera_pub import CameraPublisher


def test_http_defaults():
    """Captura lista para HTTP; MQTT desactivado por defecto."""
    cam = CameraPublisher()
    assert cam.width == 320
    assert cam.height == 240
    assert abs(cam.period - (1.0 / 15.0)) < 1e-6
    assert cam.quality == 50
    assert cam.mqtt_every == 0
    assert cam.get_jpeg() is None


def test_quality_clamped():
    """Calidad acotada 1..100."""
    assert CameraPublisher(quality=0).quality == 1
    assert CameraPublisher(quality=200).quality == 100
