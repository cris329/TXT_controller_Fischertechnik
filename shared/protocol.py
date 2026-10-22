# -*- coding: utf-8 -*-
"""MQTT topics and command helpers for Futballroboter.

Purpose: single protocol shared by PC app and TXT bridge.
Context: TXT 4.0 USB/Wi-Fi remote drive, kick and camera.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

TOPIC_DRIVE = "futball/cmd/move"
TOPIC_KICK = "futball/cmd/kick"
TOPIC_STOP = "futball/cmd/stop"
TOPIC_CAMERA = "futball/cmd/camera"
TOPIC_SOUND = "futball/cmd/sound"
TOPIC_STATUS = "futball/status"
TOPIC_FRAME = "futball/cam/jpeg"

DEFAULT_HOST = "192.168.7.2"
DEFAULT_MQTT_PORT = 3883
DEFAULT_MQTT_USER = "ft"
DEFAULT_MQTT_PASSWORD = "fischertechnik"


def clamp(value, low, high):
    """Clamp numeric value into [low, high].

    @param value: number
    @param low: minimum
    @param high: maximum
    @return: clamped number
    """
    if value < low:
        return low
    if value > high:
        return high
    return value
