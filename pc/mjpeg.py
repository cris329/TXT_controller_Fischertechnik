# -*- coding: utf-8 -*-
"""Generador MJPEG: emite solo frames nuevos (baja latencia).

Purpose: no reenviar el mismo JPEG ni esperar un periodo fijo.
Context: Flask route /camera.mjpg.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import time

from flask import Response


def mjpeg_response(get_frame, idle=0.005):
    """Multipart que espera el siguiente JPEG distinto.

    @param get_frame: callable -> bytes|None
    @param idle: float sleep cuando no hay frame nuevo
    @return: flask.Response
    """

    def generate():
        """Itera solo frames nuevos. @return: bytes chunks"""
        last = None
        while True:
            frame = get_frame()
            if frame is not None and frame is not last:
                last = frame
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            else:
                time.sleep(idle)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )
