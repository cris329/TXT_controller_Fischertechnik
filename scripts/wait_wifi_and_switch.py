# -*- coding: utf-8 -*-
"""Espera IP Wi‑Fi del TXT y valida MQTT antes de quitar el cable.

Purpose: cambiar panel de USB (192.168.7.2) a Wi‑Fi con seguridad.
Context: mlan0 debe conectarse desde la pantalla del TXT.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

from __future__ import print_function

import os
import socket
import sys
import time

import paramiko

USB_HOST = "192.168.7.2"
MQTT_PORT = 3883
USER = "ft"
PASSWORD = os.environ.get("TXT_PASSWORD", "fischertechnik")


def mqtt_ok(host, port=MQTT_PORT, timeout=2.0):
    """Prueba TCP al broker MQTT.

    @param host: str
    @param port: int
    @param timeout: float
    @return: bool
    """
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


def wifi_ip_via_usb():
    """Lee IPs de mlan0 por SSH USB.

    @return: list[str]
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(USB_HOST, username=USER, password=PASSWORD, timeout=8)
    _, stdout, _ = client.exec_command(
        "ip -4 -o addr show mlan0 2>/dev/null | awk '{print $4}'", timeout=10
    )
    raw = stdout.read().decode("utf-8", "ignore")
    client.close()
    ips = []
    for part in raw.replace("\n", " ").split():
        ip = part.split("/")[0].strip()
        if ip and not ip.startswith("127."):
            ips.append(ip)
    return ips


def main():
    """Bucle de espera hasta MQTT por Wi‑Fi. @return: int"""
    print("Cable USB: dejalo conectado.")
    print("En la PANTALLA del TXT: Ajustes -> Wi-Fi -> conecta a tu red.")
    print("Esperando IP en mlan0...")
    for _ in range(120):
        try:
            ips = wifi_ip_via_usb()
        except Exception as exc:
            print("SSH USB falló:", exc)
            time.sleep(2)
            continue
        if ips:
            host = ips[0]
            print("Wi‑Fi IP detectada:", host)
            if mqtt_ok(host):
                print("MQTT OK en", host)
                print("")
                print("YA PUEDES DESCONECTAR EL CABLE USB.")
                print("Luego arranca el panel así:")
                print('  $env:TXT_HOST="%s"; python pc\\app.py' % host)
                print("O ejecuta: scripts\\start_wifi_panel.bat")
                with open(
                    os.path.join(os.path.dirname(__file__), "wifi_host.txt"),
                    "w",
                    encoding="utf-8",
                ) as fh:
                    fh.write(host.strip() + "\n")
                return 0
            print("IP OK pero MQTT aún no responde en :3883, reintento...")
        else:
            print("... sin Wi‑Fi todavía (mlan0 sin IP)")
        time.sleep(3)
    print("Timeout: el TXT no obtuvo Wi‑Fi. Configúralo en la pantalla.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
