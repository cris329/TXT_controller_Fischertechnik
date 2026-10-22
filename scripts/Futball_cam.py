# -*- coding: utf-8 -*-
"""Camera child: HTTP MJPEG :8090 + heartbeat MQTT.

Purpose: video en vivo sin saturar Wi-Fi con MQTT JPEG.
Context: spawned by Futball.py as ftgui.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import json
import os
import sys
import time
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

CAM_PORT = 8090


def clog(msg):
    """Write camera log. @param msg: text @return: None"""
    try:
        with open("/tmp/Futball_cam.log", "a") as fh:
            fh.write("%s %s\n" % (int(time.time()), msg))
    except Exception:
        pass


def main():
    """HTTP stream + MQTT heartbeat. @return: None"""
    clog("cam main pid=%s" % os.getpid())
    import paho.mqtt.client as mqtt

    from robot.cam_http import start_cam_http
    from robot.camera_pub import CameraPublisher
    from shared.protocol import (
        DEFAULT_MQTT_PASSWORD,
        DEFAULT_MQTT_USER,
        TOPIC_FRAME,
    )

    client = mqtt.Client("FutballCam-%s" % os.getpid())
    client.username_pw_set(DEFAULT_MQTT_USER, DEFAULT_MQTT_PASSWORD)
    try:
        client.max_queued_messages_set(1)
    except Exception:
        pass
    client.connect("127.0.0.1", 3883, 60)
    client.loop_start()
    # Frames chicos + MQTT (hotspot Windows falla con HTTP largo).
    cam = CameraPublisher(
        client=client,
        topic=TOPIC_FRAME,
        width=160,
        height=120,
        fps=10,
        quality=30,
        mqtt_every=1,
    )
    cam.start()
    start_cam_http(cam.get_jpeg, port=CAM_PORT)
    clog("http+mqtt cam :%s started" % CAM_PORT)
    n = 0
    while True:
        n += 1
        if n % 5 == 0:
            client.publish(
                "futball/heartbeat",
                json.dumps({"role": "cam", "t": int(time.time()), "frames": cam.frames}),
            )
            clog("frames=%s" % cam.frames)
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        time.sleep(1)
        sys.exit(1)
