# -*- coding: utf-8 -*-
"""Servidor MJPEG HTTP en el TXT (bypass MQTT).

Purpose: video en vivo con minima latencia por Wi-Fi.
Context: Futball_cam.py escucha :8090 /cam.mjpg
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

from __future__ import print_function

import threading
import time

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer  # type: ignore

try:
    from socketserver import ThreadingMixIn
except ImportError:
    from SocketServer import ThreadingMixIn  # type: ignore


class _ThreadedServer(ThreadingMixIn, HTTPServer):
    """HTTP multi-cliente. daemon_threads evita cuelgues al salir."""

    daemon_threads = True
    allow_reuse_address = True


def start_cam_http(get_jpeg, port=8090, host="0.0.0.0"):
    """Arranca MJPEG en hilo daemon.

    @param get_jpeg: callable -> bytes|None
    @param port: int
    @param host: str bind
    @return: HTTPServer
    """

    class Handler(BaseHTTPRequestHandler):
        """Sirve /cam.mjpg y /snap.jpg."""

        def log_message(self, fmt, *args):
            return None

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/cam.mjpg", "/"):
                self._mjpeg()
            elif path == "/snap.jpg":
                self._snap()
            else:
                self.send_error(404)

        def _snap(self):
            frame = get_jpeg()
            if not frame:
                self.send_error(503)
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(frame)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(frame)
            try:
                self.wfile.flush()
            except Exception:
                pass

        def _mjpeg(self):
            self.send_response(200)
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=frame"
            )
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            last = None
            try:
                while True:
                    frame = get_jpeg()
                    if frame is not None and frame is not last:
                        last = frame
                        part = (
                            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                            + frame
                            + b"\r\n"
                        )
                        self.wfile.write(part)
                        self.wfile.flush()
                    else:
                        time.sleep(0.01)
            except Exception:
                return

    server = _ThreadedServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server
