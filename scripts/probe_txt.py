#!/usr/bin/env python3
"""Probe TXT 4.0 ft API for motors, servo and camera."""
import ft

txt = ft.fttxt2("auto")
print("TXT attrs:", [a for a in dir(txt) if not a.startswith("_")])
m = txt.motor(1)
print("motor attrs:", [a for a in dir(m) if not a.startswith("_")])
for name in ("servo", "servomotor", "cam", "camera"):
    print(name, hasattr(txt, name))
try:
    s = txt.servo(1)
    print("servo attrs:", [a for a in dir(s) if not a.startswith("_")])
except Exception as exc:
    print("servo err:", type(exc).__name__, exc)
try:
    import cv2
    cap = cv2.VideoCapture(0)
    print("camera opened:", cap.isOpened())
    if cap.isOpened():
        ok, frame = cap.read()
        print("frame:", ok, None if frame is None else frame.shape)
        cap.release()
except Exception as exc:
    print("cv2 err:", type(exc).__name__, exc)
try:
    import paho.mqtt.client as mqtt
    print("mqtt module ok", mqtt.__name__)
except Exception as exc:
    print("mqtt err:", exc)
