# -*- coding: utf-8 -*-
"""Flask dashboard: camera, buttons, keyboard API, Xbox teleop.

Purpose: drive Futballroboter from the PC browser + gamepad.
Context: MQTT control + JPEG frames (sin HTTP pull que satura hotspot).
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Flask, Response, jsonify, render_template, request

from pc.control_loop import TeleopLoop
from pc.mqtt_client import RobotMqtt
from pc.ui_assets import asset_stamp
from pc.watchdog import BridgeWatchdog
from shared.protocol import DEFAULT_HOST

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
robot = RobotMqtt(os.environ.get("TXT_HOST", DEFAULT_HOST))
teleop = TeleopLoop(robot)
watchdog = BridgeWatchdog(robot.host, robot)


@app.after_request
def _no_cache(resp):
    """Force no-cache headers. @param resp: response @return: response"""
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/")
def index():
    """Dashboard HTML. @return: HTML"""
    return render_template(
        "index.html",
        host=robot.host,
        xbox=teleop.xbox_ok,
        asset_v=asset_stamp(),
    )


@app.route("/api/drive", methods=["POST"])
def api_drive():
    """Manual drive axes. @return: JSON"""
    data = request.get_json(force=True, silent=True) or {}
    teleop.set_manual(
        float(data.get("vx", 0)),
        float(data.get("vy", 0)),
        float(data.get("omega", 0)),
    )
    return jsonify({"ok": True})


@app.route("/api/kick", methods=["POST"])
def api_kick():
    """Trigger kicker. @return: JSON"""
    teleop.request_kick()
    return jsonify({"ok": True})


@app.route("/api/sound", methods=["POST"])
def api_sound():
    """Trigger sound on the robot. @return: JSON"""
    try:
        robot.sound()
    except Exception:
        pass
    return jsonify({"ok": True})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Emergency stop. @return: JSON"""
    teleop.request_stop()
    return jsonify({"ok": True})


@app.route("/api/restart", methods=["POST"])
def api_restart():
    """Redeploy bridges on TXT. @return: JSON"""
    return jsonify({"ok": True, "msg": watchdog.restart_now()})


@app.route("/api/status")
def api_status():
    """Connection and Xbox status. @return: JSON"""
    age = robot.heartbeat_age()
    live = robot.last_frame_at is not None and (time.time() - robot.last_frame_at) < 1.5
    return jsonify({
        "mqtt": robot.status,
        "xbox": teleop.xbox_ok,
        "host": robot.host,
        "heartbeat": ("%.0fs" % age) if age is not None else "offline",
        "video": live,
        "restart": watchdog.last_msg,
    })


@app.route("/camera.jpg")
def camera_jpg():
    """Ultimo JPEG MQTT (buffer local). @return: image/jpeg|204"""
    frame = robot.get_frame()
    if not frame:
        return ("", 204)
    return Response(frame, mimetype="image/jpeg")


def main():
    """Boot MQTT, teleop, watchdog and Flask. @return: None"""
    try:
        robot.start()
    except Exception:
        robot.status = "offline"
    teleop.start()
    threading.Thread(target=watchdog.auto_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5055, debug=False, threaded=True)


if __name__ == "__main__":
    main()
