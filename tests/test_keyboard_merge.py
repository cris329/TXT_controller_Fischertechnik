# -*- coding: utf-8 -*-
"""Espejo de mergeKeyAxes (keyboard.js): giro atenuado al avanzar.

Purpose: validar regla avance+giro de flechas.
Context: panel PC teleop por teclado.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

TURN_MOVING = 0.4


def merge_key_axes(codes, axes):
    """Suma ejes y atenua omega si hay traslacion.

    @param codes: iterable de codigos
    @param axes: dict code -> (vx, vy, omega)
    @return: tuple (vx, vy, omega)
    """
    vx = vy = omega = 0.0
    for code in codes:
        a = axes.get(code)
        if not a:
            continue
        vx += a[0]
        vy += a[1]
        omega += a[2]
    vx = max(-1.0, min(1.0, vx))
    vy = max(-1.0, min(1.0, vy))
    omega = max(-1.0, min(1.0, omega))
    if (abs(vx) > 0.05 or abs(vy) > 0.05) and omega:
        omega *= TURN_MOVING
    return vx, vy, omega


AXES = {
    "ArrowUp": (1, 0, 0),
    "ArrowDown": (-1, 0, 0),
    "ArrowLeft": (0, 0, -1),
    "ArrowRight": (0, 0, 1),
}


def test_arrow_up_only():
    """Solo arriba avanza sin giro."""
    assert merge_key_axes(["ArrowUp"], AXES) == (1.0, 0.0, 0.0)


def test_arrow_left_only():
    """Solo izquierda gira a fondo."""
    assert merge_key_axes(["ArrowLeft"], AXES) == (0.0, 0.0, -1.0)


def test_up_and_left_attenuates_turn():
    """Arriba+izquierda: avance con giro atenuado."""
    vx, vy, omega = merge_key_axes(["ArrowUp", "ArrowLeft"], AXES)
    assert vx == 1.0
    assert vy == 0.0
    assert abs(omega - (-TURN_MOVING)) < 1e-9


def test_release_all_stops():
    """Sin teclas: detenido."""
    assert merge_key_axes([], AXES) == (0.0, 0.0, 0.0)
