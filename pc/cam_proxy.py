# -*- coding: utf-8 -*-
"""Proxy MJPEG desde el TXT HTTP :8090 (baja latencia).

Purpose: el navegador habla con Flask; Flask tira del TXT en vivo.
Context: fallback a MQTT latest_frame si HTTP falla.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import time
import urllib.error
import urllib.request

from flask import Response


def proxy_mjpeg(host, port=8090, fallback=None, idle=0.01):
    """Proxy multipart desde http://host:port/cam.mjpg.

    @param host: str IP TXT
    @param port: int
    @param fallback: callable -> bytes|None
    @param idle: float
    @return: flask.Response
    """
    url = "http://%s:%s/cam.mjpg" % (host, port)

    def generate():
        """Reenvia bytes del TXT o fallback MQTT. @return: bytes"""
        while True:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=8) as resp:
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        yield chunk
            except Exception:
                if fallback:
                    frame = fallback()
                    if frame:
                        yield (
                            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                            + frame
                            + b"\r\n"
                        )
                time.sleep(0.2)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


def snap_ok(host, port=8090, timeout=1.2):
    """True si el TXT entrega un JPEG fresco.

    @param host: str
    @param port: int
    @param timeout: float
    @return: bool
    """
    try:
        url = "http://%s:%s/snap.jpg" % (host, port)
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read(64)
            return bool(data) and len(data) > 20
    except (urllib.error.URLError, OSError, ValueError):
        return False
