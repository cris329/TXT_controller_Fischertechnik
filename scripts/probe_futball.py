# -*- coding: utf-8 -*-
"""Foreground smoke test for Futball imports and start."""
from __future__ import print_function
import os
import sys
import traceback

BASE = "/opt/ft/workspaces/Futball"
os.chdir(BASE)
sys.path.insert(0, BASE)
print("cwd", os.getcwd(), flush=True)
print("files", os.listdir(BASE), flush=True)

try:
    print("1 ftlock", flush=True)
    import ftlock
    ftlock.notify("R")
    print("2 hardware", flush=True)
    from robot.hardware import RobotHardware
    h = RobotHardware()
    print("3 mqtt", flush=True)
    import paho.mqtt.client as mqtt
    from robot.camera_pub import CameraPublisher
    from robot.mqtt_bridge import CommandBridge
    from shared.protocol import TOPIC_FRAME
    c = mqtt.Client("probe-%s" % os.getpid())
    c.username_pw_set("ft", "fischertechnik")
    c.connect("127.0.0.1", 3883, 60)
    c.loop_start()
    cam = CameraPublisher(c, TOPIC_FRAME)
    cam.start()
    print("4 camera started", flush=True)
    import time
    for i in range(10):
        time.sleep(1)
        print("tick", i, "frames", cam.frames, flush=True)
    print("OK", flush=True)
except Exception:
    traceback.print_exc()
    sys.exit(1)
