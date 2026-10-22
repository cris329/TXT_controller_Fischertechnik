# -*- coding: utf-8 -*-
"""Captura JPEG en memoria (+ MQTT opcional).

Purpose: buffer local para HTTP MJPEG; MQTT solo si hace falta.
Context: VideoStream ftgui / Futball_cam.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import threading
import time


class CameraPublisher(object):
    """Captura continua; latest JPEG listo para HTTP."""

    def __init__(
        self, client=None, topic="", width=320, height=240, fps=15, quality=50, mqtt_every=0
    ):
        """Crea publicador.

        @param client: mqtt client|None
        @param topic: str MQTT
        @param width: int
        @param height: int
        @param fps: int
        @param quality: int 1-100
        @param mqtt_every: 0=off, N=publicar 1 de cada N frames
        """
        self.client = client
        self.topic = topic
        self.width = width
        self.height = height
        self.quality = int(max(1, min(100, quality)))
        self.period = 1.0 / float(max(1, fps))
        self.mqtt_every = int(max(0, mqtt_every))
        self._on = False
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self.latest = None
        self.frames = 0

    def get_jpeg(self):
        """Ultimo JPEG. @return: bytes|None"""
        with self._lock:
            return self.latest

    def start(self):
        """Start capture thread. @return: None"""
        if self._thread and self._thread.is_alive():
            self._on = True
            return
        self._stop.clear()
        self._on = True
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Stop capture. @return: None"""
        self._on = False
        self._stop.set()

    def _open_stream(self):
        """Open VideoStream. @return: VideoStream"""
        from fischertechnik.camera.VideoStream import VideoStream

        stream = VideoStream.getInstance()
        stream.set_width(self.width)
        stream.set_height(self.height)
        stream.set_fps(max(1, int(round(1.0 / self.period))))
        stream.start()
        time.sleep(0.35)
        return stream

    def _grab_newest(self, stream, flush=5):
        """Mas reciente del buffer cam. @param stream: obj @param flush: int @return: tuple"""
        ok, frame = False, None
        for _ in range(max(1, flush)):
            ok_i, fr = stream.read()
            if ok_i and fr is not None:
                ok, frame = True, fr
        return ok, frame

    def _loop(self):
        """Capture loop. @return: None"""
        import cv2

        stream = None
        fails = 0
        next_t = time.time()
        while not self._stop.is_set():
            if not self._on:
                time.sleep(0.1)
                continue
            try:
                if stream is None:
                    stream = self._open_stream()
                    next_t = time.time()
                ok, frame = self._grab_newest(stream)
                if not ok or frame is None:
                    fails += 1
                    if fails >= 15:
                        self._safe_stop(stream)
                        stream = None
                        fails = 0
                    time.sleep(0.015)
                    continue
                fails = 0
                ok2, buf = cv2.imencode(
                    ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                )
                if ok2:
                    payload = buf.tostring() if hasattr(buf, "tostring") else buf.tobytes()
                    with self._lock:
                        self.latest = payload
                    self.frames += 1
                    if (
                        self.client
                        and self.topic
                        and self.mqtt_every
                        and self.frames % self.mqtt_every == 0
                    ):
                        self.client.publish(self.topic, payload, qos=0)
                next_t += self.period
                delay = next_t - time.time()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_t = time.time()
            except Exception:
                self._safe_stop(stream)
                stream = None
                time.sleep(0.4)
        self._safe_stop(stream)

    @staticmethod
    def _safe_stop(stream):
        """Stop stream. @param stream: obj|None @return: None"""
        if stream is None:
            return
        try:
            stream.stop()
        except Exception:
            pass
