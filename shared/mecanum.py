# -*- coding: utf-8 -*-
"""Mecanum kinematics for Futballroboter (4 wheels).

Purpose: convert vx/vy/omega into M1..M4 PWM speeds.
Context: omnidirectional soccer robot on TXT 4.0.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from shared.protocol import clamp


def mecanum_speeds(vx, vy, omega, max_pwm=512):
    """Map normalized axes to four motor PWM values.

    Motor order: M1 front-left, M2 front-right, M3 rear-left, M4 rear-right.
    Positive vx = forward, vy = strafe right, omega = rotate clockwise.

    @param vx: forward axis in [-1, 1]
    @param vy: strafe axis in [-1, 1]
    @param omega: rotation axis in [-1, 1]
    @param max_pwm: absolute PWM limit (default 512)
    @return: tuple (m1, m2, m3, m4) as ints
    @example mecanum_speeds(1, 0, 0) -> forward
    """
    vx = clamp(float(vx), -1.0, 1.0)
    vy = clamp(float(vy), -1.0, 1.0)
    omega = clamp(float(omega), -1.0, 1.0)
    raw = (
        vx - vy - omega,
        vx + vy + omega,
        vx + vy - omega,
        vx - vy + omega,
    )
    peak = max([abs(v) for v in raw] + [1.0])
    return tuple(int(round((v / peak) * max_pwm)) for v in raw)
