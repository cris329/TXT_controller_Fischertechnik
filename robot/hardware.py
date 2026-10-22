# -*- coding: utf-8 -*-
"""TXT 4.0 actuators for Futballroboter.

Purpose: drive M1-M4 and kick ball with servo (S1..S3).
Context: ROBO Pro shot=400 rest=250; pulse all servo ports.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os
import subprocess
import threading
import time

import ft
import ftlock

KICK_LEVEL = 400
REST_LEVEL = 250
HOLD_S = 0.6

SOUND_FILE = "/usr/share/sounds/qtmenu/05_Car_horn_long.wav"


class RobotHardware(object):
    """Owns motors and kicker servos on the TXT 4.0."""

    def __init__(self):
        """Open controller lock and create motor/servo handles."""
        ftlock.notify("R")
        self.txt = ft.fttxt2("auto")
        self.motors = [self.txt.motor(i) for i in range(1, 5)]
        # Pulse S1+S2+S3 so a mis-plugged kicker still moves
        self.servos = [self.txt.servo(i) for i in range(1, 4)]
        self.servo_index = 1
        self._kick_lock = threading.Lock()
        self.last_kick_pwm = None
        self._set_all(REST_LEVEL)

    def _set_one(self, servo, level):
        """Set one servo to ROBO Pro level 0..512.

        @param servo: ft servo handle
        @param level: int
        @return: None
        """
        level = max(0, min(512, int(level)))
        servo.setLevel(level)
        try:
            servo.pwm_set(level)
        except Exception:
            pass
        try:
            us = 610 + int((level * (2360 - 610)) / 512.0)
            servo.setLevelUs(us)
        except Exception:
            pass

    def _set_all(self, level):
        """Set every servo port to the same level.

        @param level: int 0..512
        @return: int pwm of S1
        """
        for servo in self.servos:
            self._set_one(servo, level)
        self.last_kick_pwm = getattr(self.servos[0], "pwm", None)
        return self.last_kick_pwm

    def set_speeds(self, speeds):
        """Apply four PWM speeds to M1..M4.

        @param speeds: iterable of 4 ints in [-512, 512]
        @return: None
        """
        for motor, speed in zip(self.motors, speeds):
            motor.setSpeed(int(speed))

    def stop(self):
        """Stop all drive motors.

        @return: None
        """
        self.set_speeds((0, 0, 0, 0))

    def kick(self):
        """Fire kicker pulse on S1-S3 in background.

        @return: None
        """
        if not self._kick_lock.acquire(False):
            return
        threading.Thread(target=self._kick_run, daemon=True).start()

    def _kick_run(self):
        """Move to 400 (shot) then back to 250 (rest).

        @return: None
        """
        try:
            self._set_all(REST_LEVEL)
            time.sleep(0.1)
            self._set_all(KICK_LEVEL)
            time.sleep(HOLD_S)
            self._set_all(REST_LEVEL)
        finally:
            self._kick_lock.release()

    def close(self):
        """Release hardware safely.

        @return: None
        """
        try:
            self.stop()
            self._set_all(REST_LEVEL)
        finally:
            self.txt.close()

    def buzzer(self):
        """Play a short sound through the TXT speaker via aplay.

        Runs in a background thread so the MQTT loop is not blocked.
        Sets the speaker volume to maximum first.

        @return: None
        """
        threading.Thread(target=self._play_sound, daemon=True).start()

    def _play_sound(self):
        """Set volume to max then play SOUND_FILE with aplay.

        @return: None
        """
        try:
            for ctl in ("Speaker", "Speaker Driver", "Speaker Analog", "DAC"):
                subprocess.call(
                    ["amixer", "-D", "default", "sset", ctl, "100%"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            rc1 = subprocess.call(
                ["amixer", "-D", "default", "sset", "Speaker", "unmute"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            rc2 = subprocess.call(
                ["aplay", "-D", "default", SOUND_FILE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            with open("/opt/ft/workspaces/Futball/sound_debug.log", "a") as f:
                f.write("amixer_rc=%s aplay_rc=%s\n" % (rc1, rc2))
        except Exception as e:
            try:
                with open("/opt/ft/workspaces/Futball/sound_debug.log", "a") as f:
                    f.write("ERROR: %s\n" % e)
            except Exception:
                pass
