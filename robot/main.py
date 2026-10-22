# -*- coding: utf-8 -*-
"""TXT 4.0 Futballroboter MQTT bridge entrypoint.

Purpose: run on controller, expose drive/kick/camera over MQTT.
Context: start with sudo -u ftgui for camera access.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import logging
import time

import paho.mqtt.client as mqtt

from robot.camera_pub import CameraPublisher
from robot.hardware import RobotHardware
from robot.mqtt_bridge import CommandBridge
from shared.protocol import (
    DEFAULT_MQTT_PASSWORD,
    DEFAULT_MQTT_USER,
    TOPIC_FRAME,
    TOPIC_STATUS,
)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("futball.main")


def main():
    """Start hardware, camera publisher and MQTT loop.

    @return: None
    """
    hardware = RobotHardware()
    client = mqtt.Client(client_id="futball-bridge")
    client.username_pw_set(DEFAULT_MQTT_USER, DEFAULT_MQTT_PASSWORD)
    camera = CameraPublisher(client, TOPIC_FRAME)
    bridge = CommandBridge(hardware, camera)

    def on_connect(client, userdata, flags, rc):
        LOG.info("mqtt connected rc=%s", rc)
        for topic in bridge.topics():
            client.subscribe(topic)
        client.publish(TOPIC_STATUS, bridge.status_payload(), retain=True)
        camera.start()

    def on_message(client, userdata, msg):
        bridge.handle(msg.topic, msg.payload)

    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect("127.0.0.1", 3883, 60)
        client.loop_start()
        LOG.info("Futballroboter bridge running")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("stopping")
    finally:
        camera.stop()
        client.loop_stop()
        client.disconnect()
        hardware.close()


if __name__ == "__main__":
    main()
