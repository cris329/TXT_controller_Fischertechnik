@echo off
echo Abriendo panel en puerto NUEVO 5055 (ventana InPrivate)...
start msedge --inprivate "http://127.0.0.1:5055/?fresh=%RANDOM%"
exit
