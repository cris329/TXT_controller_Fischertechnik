# -*- coding: utf-8 -*-
"""Camera MQTT publisher using fischertechnik VideoStream."""
from __future__ import print_function
import json
import os
import sys
import time
import traceback


def p(msg):
    print(msg, flush=True)


def main():
    p("1 start pid=%s" % os.getpid())
    import cv2
    import paho.mqtt.client as mqtt
    from fischertechnik.camera.VideoStream import VideoStream

    client = mqtt.Client("futball-cam-%s" % os.getpid())
    client.username_pw_set("ft", "fischertechnik")
    client.connect("127.0.0.1", 3883, 60)
    client.loop_start()
    p("2 mqtt ok")

    stream = VideoStream.getInstance()
    stream.set_width(320)
    stream.set_height(240)
    stream.set_fps(8)
    stream.start()
    p("3 stream running=%s" % stream.is_running())
    time.sleep(1.5)

    n = 0
    fails = 0
    while True:
        ok, frame = stream.read()
        if not ok or frame is None:
            fails += 1
            if fails >= 30:
                p("restart stream")
                try:
                    stream.stop()
                except Exception:
                    pass
                time.sleep(1)
                stream = VideoStream.getInstance()
                stream.start()
                fails = 0
            time.sleep(0.2)
            continue
        fails = 0
        ok2, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
        if ok2:
            payload = buf.tostring()
            client.publish("futball/cam/jpeg", payload)
            n += 1
            if n <= 5 or n % 20 == 0:
                p("frames %s size=%s" % (n, len(payload)))
            if n % 10 == 0:
                client.publish(
                    "futball/heartbeat",
                    json.dumps({"role": "cam", "t": int(time.time()), "n": n}),
                )
        time.sleep(0.12)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        time.sleep(2)
        sys.exit(1)
