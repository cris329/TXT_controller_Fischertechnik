# -*- coding: utf-8 -*-
"""MQTT command handler for Futballroboter bridge.

Purpose: map drive/kick/stop/camera topics to hardware.
Context: TXT Mosquitto broker port 3883 / localhost 2883.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import json
import logging

from shared.mecanum import mecanum_speeds
from shared.protocol import (
    TOPIC_CAMERA,
    TOPIC_DRIVE,
    TOPIC_FRAME,
    TOPIC_KICK,
    TOPIC_SOUND,
    TOPIC_STATUS,
    TOPIC_STOP,
)

LOG = logging.getLogger("futball.bridge")


class CommandBridge(object):
    """Translate MQTT messages into robot actions."""

    def __init__(self, hardware, camera):
        """Bind hardware and camera publisher.

        @param hardware: RobotHardware instance
        @param camera: CameraPublisher instance
        """
        self.hardware = hardware
        self.camera = camera

    def topics(self):
        """List subscribed command topics.

        @return: list of str
        """
        return [TOPIC_DRIVE, TOPIC_KICK, TOPIC_STOP, TOPIC_CAMERA, TOPIC_SOUND]

    def handle(self, topic, payload):
        """Dispatch one MQTT message.

        @param topic: str
        @param payload: bytes
        @return: None
        """
        try:
            if topic == TOPIC_STOP or topic.endswith("/stop"):
                self.hardware.stop()
            elif topic == TOPIC_KICK or topic.endswith("/kick"):
                LOG.info("kick")
                self.hardware.kick()
            elif topic == TOPIC_SOUND:
                # brief beep using the TXT buzzer (if available)
                try:
                    self.hardware.buzzer()
                except Exception:
                    pass
            elif topic == TOPIC_DRIVE or topic.endswith("/move"):
                self._drive(payload)
            elif topic == TOPIC_CAMERA or topic.endswith("/camera"):
                self._camera(payload)
        except Exception:
            LOG.exception("command failed topic=%s", topic)

    def _drive(self, payload):
        data = json.loads(payload.decode("utf-8"))
        speeds = mecanum_speeds(
            data.get("vx", 0),
            data.get("vy", 0),
            data.get("omega", 0),
            int(data.get("max_pwm", 512)),
        )
        self.hardware.set_speeds(speeds)

    def _camera(self, payload):
        data = json.loads(payload.decode("utf-8"))
        if data.get("on", True):
            self.camera.start()
        else:
            self.camera.stop()

    def status_payload(self):
        """Build JSON status body.

        @return: str
        """
        return json.dumps({"ok": True, "cam": TOPIC_FRAME})
