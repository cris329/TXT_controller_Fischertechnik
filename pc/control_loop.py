# -*- coding: utf-8 -*-
"""Merge Xbox/keyboard intents and publish to robot.

Purpose: continuous teleop loop for Futballroboter.
Context: background thread inside Flask PC app.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import threading
import time

from pc.xbox_input import XboxController


class TeleopLoop(object):
    """Poll inputs and send MQTT drive/kick/stop."""

    def __init__(self, robot_mqtt):
        """Create teleop with MQTT facade.

        @param robot_mqtt: RobotMqtt instance
        """
        self.robot = robot_mqtt
        self.xbox = XboxController()
        self.manual = {"vx": 0.0, "vy": 0.0, "omega": 0.0}
        self._manual_prio_until = 0.0
        self._kick_latched = False
        self._stop = threading.Event()
        self._thread = None
        self.xbox_ok = False

    def start(self):
        """Start teleop thread (pygame en este hilo). @return: None"""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def set_manual(self, vx=0.0, vy=0.0, omega=0.0):
        """UI/teclado: prioridad breve sobre Xbox.

        @param vx: float @param vy: float @param omega: float
        """
        self.manual = {"vx": vx, "vy": vy, "omega": omega}
        # Teclado gana ~0.4s para que el pad no pise flechas/WASD.
        self._manual_prio_until = time.time() + 0.4
        self.robot.drive(vx, vy, omega)

    def request_kick(self):
        """Kick from UI. @return: None"""
        self.robot.kick()

    def request_stop(self):
        """Stop from UI. @return: None"""
        self.manual = {"vx": 0.0, "vy": 0.0, "omega": 0.0}
        self.robot.stop_motors()

    def stop(self):
        """End teleop thread. @return: None"""
        self._stop.set()
        self.xbox.close()

    def _pick_axes(self, pad):
        """Elige teclado o Xbox. @param pad: dict @return: tuple"""
        m = self.manual
        if time.time() < self._manual_prio_until:
            return (m["vx"], m["vy"], m["omega"])
        if pad["connected"] and (pad["vx"] or pad["vy"] or pad["omega"]):
            return (pad["vx"], pad["vy"], pad["omega"])
        return (m["vx"], m["vy"], m["omega"])

    def _run(self):
        """Xbox prioridad; reenvio periodico por Wi-Fi."""
        self.xbox_ok = self.xbox.open()
        last = None
        ticks = 0
        while not self._stop.is_set():
            ticks += 1
            if ticks % 20 == 0 and not self.xbox_ok:
                self.xbox_ok = self.xbox.ensure()
            pad = self.xbox.poll()
            self.xbox_ok = bool(pad.get("connected"))
            axes = self._pick_axes(pad)
            moving = axes != (0.0, 0.0, 0.0)
            # Reenviar cada ~200ms en movimiento (paquetes MQTT perdidos en hotspot).
            if axes != last or (moving and ticks % 4 == 0):
                self.robot.drive(axes[0], axes[1], axes[2])
                last = axes
            if pad.get("kick") and not self._kick_latched:
                self.robot.kick()
                self._kick_latched = True
            if not pad.get("kick"):
                self._kick_latched = False
            if pad.get("stop"):
                self.robot.stop_motors()
                last = (0.0, 0.0, 0.0)
            time.sleep(0.05)
