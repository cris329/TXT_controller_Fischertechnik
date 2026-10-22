# -*- coding: utf-8 -*-
"""Hilo que tira snaps del TXT a un buffer local (UI sin esperar Wi-Fi).

Purpose: el navegador lee JPEG instantaneo del PC; el pull va en background.
Context: hotspot Windows con timeouts intermitentes a :8090.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

import http.client
import threading
import time


class CamPuller(object):
    """Actualiza latest JPEG desde http://host:8090/snap.jpg."""

    def __init__(self, host, port=8090, period=0.08):
        """@param host: str @param port: int @param period: float"""
        self.host = host
        self.port = port
        self.period = period
        self.latest = None
        self.last_ok = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        """Start pull loop. @return: None"""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop pull loop. @return: None"""
        self._stop.set()

    def get_jpeg(self):
        """JPEG cacheado. @return: bytes|None"""
        with self._lock:
            return self.latest

    def is_live(self, max_age=1.2):
        """True si hubo snap reciente. @param max_age: float @return: bool"""
        if self.last_ok is None:
            return False
        return (time.time() - self.last_ok) < max_age

    def _loop(self):
        """Pull continuo. @return: None"""
        while not self._stop.is_set():
            try:
                conn = http.client.HTTPConnection(self.host, self.port, timeout=0.9)
                conn.request("GET", "/snap.jpg", headers={"Connection": "close"})
                resp = conn.getresponse()
                data = resp.read()
                conn.close()
                if resp.status == 200 and data and len(data) > 80:
                    with self._lock:
                        self.latest = data
                        self.last_ok = time.time()
            except Exception:
                pass
            time.sleep(self.period)
