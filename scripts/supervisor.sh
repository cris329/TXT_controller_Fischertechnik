#!/bin/sh
# Keep Futballroboter bridges alive forever (drive + camera).
REMOTE=/opt/ft/workspaces/futball
export PYTHONPATH="$REMOTE"
LOG=/tmp/futball_supervisor.log

log() { echo "$(date) $*" >> "$LOG"; }

kill_old() {
  ps > /tmp/futball_ps.txt
  while read -r line; do
    case "$line" in
      *boot.py*|*boot_camera.py*)
        set -- $line
        kill -9 "$1" 2>/dev/null
        ;;
    esac
  done < /tmp/futball_ps.txt
}

run_loop() {
  name="$1"
  script="$2"
  logfile="$3"
  while true; do
    log "start $name"
    : > "$logfile"
    /usr/bin/python3 -u "$script" >> "$logfile" 2>&1
    code=$?
    log "exit $name code=$code — restart in 2s"
    sleep 2
  done
}

kill_old
sleep 1
: > "$LOG"
log "supervisor pid=$$"
run_loop drive "$REMOTE/boot.py" /tmp/futball_run.log &
sleep 4
run_loop camera "$REMOTE/boot_camera.py" /tmp/futball_cam.log &

# Never exit: keep supervisor shell alive even if wait semantics change.
while true; do
  sleep 15
  # Relaunch missing loops if somehow gone (best-effort).
  ps > /tmp/futball_ps2.txt
  drive_ok=0
  cam_ok=0
  while read -r line; do
    case "$line" in
      *boot.py*) drive_ok=1 ;;
      *boot_camera.py*) cam_ok=1 ;;
    esac
  done < /tmp/futball_ps2.txt
  if [ "$drive_ok" -eq 0 ]; then
    log "watchdog relaunch drive"
    run_loop drive "$REMOTE/boot.py" /tmp/futball_run.log &
  fi
  if [ "$cam_ok" -eq 0 ]; then
    log "watchdog relaunch camera"
    run_loop camera "$REMOTE/boot_camera.py" /tmp/futball_cam.log &
  fi
done
