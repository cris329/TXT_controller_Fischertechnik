# -*- coding: utf-8 -*-
"""PC MQTT client for Futballroboter commands and camera.

Purpose: publish drive/kick and receive JPEG frames.
Context: Windows app talking to TXT Mosquitto :3883.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import json
import os
import threading
import time

import paho.mqtt.client as mqtt

from shared.protocol import (
    DEFAULT_HOST,
    DEFAULT_MQTT_PASSWORD,
    DEFAULT_MQTT_PORT,
    DEFAULT_MQTT_USER,
    TOPIC_CAMERA,
    TOPIC_DRIVE,
    TOPIC_FRAME,
    TOPIC_KICK,
    TOPIC_SOUND,
    TOPIC_STATUS,
    TOPIC_STOP,
)


class RobotMqtt(object):
    """Thread-safe MQTT facade for the dashboard."""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_MQTT_PORT):
        """Connect settings for TXT broker.

        @param host: TXT IP
        @param port: MQTT port
        """
        self.host = host
        self.port = port
        self.latest_frame = None
        self.status = "disconnected"
        self.last_heartbeat = None
        self.last_frame_at = None
        self._lock = threading.Lock()
        client_id = "futball-pc-%s" % os.getpid()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.username_pw_set(DEFAULT_MQTT_USER, DEFAULT_MQTT_PASSWORD)
        try:
            self.client.max_queued_messages_set(1)
        except Exception:
            pass
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start(self):
        """Connect async so the UI boots even if TXT is offline.

        @return: None
        """
        self.status = "connecting"
        try:
            self.client.connect_async(self.host, self.port, 60)
        except Exception:
            self.status = "offline"
        self.client.loop_start()

    def stop(self):
        """Disconnect cleanly.

        @return: None
        """
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        ok = reason_code == 0 or str(reason_code) == "Success"
        self.status = "connected" if ok else "error"
        client.subscribe("futball/#")
        client.publish(TOPIC_CAMERA, json.dumps({"on": True}))

    def _on_message(self, client, userdata, msg):
        if msg.topic == TOPIC_FRAME or msg.topic.endswith("/jpeg"):
            with self._lock:
                self.latest_frame = msg.payload
                self.last_frame_at = time.time()
        elif msg.topic == TOPIC_STATUS:
            self.status = msg.payload.decode("utf-8", errors="ignore")
        elif msg.topic.endswith("heartbeat"):
            self.last_heartbeat = time.time()

    def heartbeat_age(self):
        """Seconds since last drive/cam heartbeat or frame.

        @return: float|None
        """
        marks = [t for t in (self.last_heartbeat, self.last_frame_at) if t]
        if not marks:
            return None
        return time.time() - max(marks)

    def drive(self, vx, vy, omega, max_pwm=512):
        """Publish mecanum drive command.

        @param vx: forward [-1,1]
        @param vy: strafe [-1,1]
        @param omega: rotate [-1,1]
        @param max_pwm: PWM cap
        @return: None
        """
        body = {"vx": vx, "vy": vy, "omega": omega, "max_pwm": max_pwm}
        self.client.publish(TOPIC_DRIVE, json.dumps(body))

    def kick(self):
        """Publish kick command.

        @return: None
        """
        self.client.publish(TOPIC_KICK, b"1")

    def stop_motors(self):
        """Publish emergency stop.

        @return: None
        """
        self.client.publish(TOPIC_STOP, b"1")

    def sound(self):
        """Publish sound command.

        @return: None
        """
        self.client.publish(TOPIC_SOUND, b"1")

    def get_frame(self):
        """Return latest JPEG bytes or None.

        @return: bytes|None
        """
        with self._lock:
            return self.latest_frame
