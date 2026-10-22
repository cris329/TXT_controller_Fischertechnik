#!/bin/sh
# Start Futballroboter MQTT bridges via allowed sudo python3 target.
REMOTE=/opt/ft/workspaces/futball
pkill -f "$REMOTE/boot.py" 2>/dev/null || true
pkill -f "$REMOTE/boot_camera.py" 2>/dev/null || true
sleep 1
sudo -u ftgui /usr/bin/python3 -u "$REMOTE/launch_detached.py"
sleep 3
echo "DRIVE_LOG"
cat /tmp/futball_run.log 2>/dev/null || true
echo "CAM_LOG"
cat /tmp/futball_cam.log 2>/dev/null || true
echo "PROCS"
ps | grep -E 'boot.py|boot_camera' | grep -v grep || true
