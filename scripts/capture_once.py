# -*- coding: utf-8 -*-
"""Take one JPEG from USB camera and exit (crash-safe)."""
from __future__ import print_function
import sys

import cv2

out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/futball_frame.jpg"
cap = cv2.VideoCapture(0)
ok, frame = cap.read()
cap.release()
if not ok:
    sys.exit(2)
frame = cv2.resize(frame, (320, 240))
ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
if not ok:
    sys.exit(3)
open(out, "wb").write(buf.tostring())
sys.exit(0)
