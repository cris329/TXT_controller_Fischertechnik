# -*- coding: utf-8 -*-
"""Xbox / XInput gamepad reader via pygame.

Purpose: map sticks and buttons to robot axes and kick.
Context: Windows PC; giro atenuado al avanzar (mejor mezcla).
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os

from shared.protocol import clamp

DEADZONE = 0.20
# Al avanzar/strafe, el giro no debe anular el avance (mecanum).
TURN_SCALE = 0.55
TURN_SCALE_MOVING = 0.40


def _dz(value):
    """Apply stick deadzone. @param value: float @return: float"""
    return 0.0 if abs(value) < DEADZONE else clamp(value, -1.0, 1.0)


class XboxController(object):
    """Read one pygame joystick as Xbox-style pad."""

    def __init__(self):
        """Lazy-init pygame joystick subsystem."""
        self.joy = None
        self._pygame = None
        self._name = ""

    def open(self):
        """Open first joystick (mismo hilo que poll). @return: bool"""
        os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")
        import pygame

        self._pygame = pygame
        if not pygame.get_init():
            pygame.init()
        if pygame.joystick.get_init():
            pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() < 1:
            self.joy = None
            self._name = ""
            return False
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()
        self._name = self.joy.get_name()
        return True

    def ensure(self):
        """Reabre si hace falta. @return: bool"""
        try:
            if self.joy and self.joy.get_init():
                return True
        except Exception:
            self.joy = None
        return self.open()

    def poll(self):
        """Return drive axes and buttons.

        @return: dict vx, vy, omega, kick, stop, connected
        """
        empty = {
            "vx": 0.0, "vy": 0.0, "omega": 0.0,
            "kick": False, "stop": False, "connected": False,
        }
        if not self.ensure() or not self.joy or not self._pygame:
            return empty
        for _event in self._pygame.event.get():
            pass
        n = self.joy.get_numaxes()
        vy = _dz(self.joy.get_axis(0)) if n > 0 else 0.0
        vx = _dz(-self.joy.get_axis(1)) if n > 1 else 0.0
        # Stick derecho X = giro (eje 2 en XInput/DI de 6 ejes).
        omega_raw = _dz(self.joy.get_axis(2)) if n > 2 else 0.0
        moving = abs(vx) > 0.05 or abs(vy) > 0.05
        scale = TURN_SCALE_MOVING if moving else TURN_SCALE
        omega = clamp(omega_raw * scale, -1.0, 1.0)
        nb = self.joy.get_numbuttons()
        kick = bool(
            (nb > 0 and self.joy.get_button(0))
            or (nb > 5 and self.joy.get_button(5))
        )
        stop = bool(
            (nb > 1 and self.joy.get_button(1))
            or (nb > 6 and self.joy.get_button(6))
        )
        return {
            "vx": vx, "vy": vy, "omega": omega,
            "kick": kick, "stop": stop, "connected": True,
        }

    def close(self):
        """Release joystick. @return: None"""
        self.joy = None
        if self._pygame and self._pygame.joystick.get_init():
            try:
                self._pygame.joystick.quit()
            except Exception:
                pass
