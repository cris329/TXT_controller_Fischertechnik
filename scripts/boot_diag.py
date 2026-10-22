# -*- coding: utf-8 -*-
"""Drive/kick MQTT bridge for TXT 4.0 Futballroboter."""
from __future__ import print_function
import json
import os
import sys
import time
import traceback

sys.path.insert(0, "/opt/ft/workspaces/futball")


def p(msg):
    print(msg, flush=True)


def main():
    p("1 start pid=%s" % os.getpid())
    import ft
    import ftlock
    from shared.mecanum import mecanum_speeds
    import paho.mqtt.client as mqtt

    ftlock.notify("R")
    txt = ft.fttxt2("auto")
    motors = [txt.motor(i) for i in range(1, 5)]
    servo = txt.servo(1)
    p("2 hardware")
    client = mqtt.Client("futball-bridge-%s" % os.getpid())
    client.username_pw_set("ft", "fischertechnik")

    def on_connect(client, userdata, flags, rc):
        p("3 mqtt rc=%s" % rc)
        client.subscribe("futball/cmd/#")
        client.publish(
            "futball/status",
            json.dumps({"ok": True, "role": "drive", "pid": os.getpid()}),
            retain=True,
        )

    def on_message(client, userdata, msg):
        try:
            p("cmd %s" % msg.topic)
            if msg.topic.endswith("move"):
                data = json.loads(msg.payload.decode("utf-8"))
                speeds = mecanum_speeds(
                    data.get("vx", 0),
                    data.get("vy", 0),
                    data.get("omega", 0),
                    int(data.get("max_pwm", 350)),
                )
                for motor, speed in zip(motors, speeds):
                    motor.setSpeed(int(speed))
            elif msg.topic.endswith("stop"):
                for motor in motors:
                    motor.setSpeed(0)
            elif msg.topic.endswith("kick"):
                servo.setLevel(400)
                time.sleep(0.25)
                servo.setLevel(250)
        except Exception:
            traceback.print_exc()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 3883, 60)
    client.loop_start()
    p("4 ready")
    beat = 0
    while True:
        beat += 1
        if beat % 5 == 0:
            client.publish(
                "futball/heartbeat",
                json.dumps({"role": "drive", "t": int(time.time()), "n": beat}),
            )
            p("heartbeat %s" % beat)
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        time.sleep(2)
        sys.exit(1)
