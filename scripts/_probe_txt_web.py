# -*- coding: utf-8 -*-
"""Probe TXT Angular bundle for WiFi-related API paths (no secrets)."""
import re
import urllib.request

js = urllib.request.urlopen(
    "http://192.168.7.2/main-es2015.003d0ee452a0da7d4c67.js", timeout=20
).read().decode("utf-8", "ignore")
print("len", len(js))
for pat in ("wifi", "WiFi", "wlan", "ssid", "/api/", "network"):
    print(pat, js.lower().count(pat.lower()))
urls = sorted(set(re.findall(r"['\"](/[A-Za-z0-9_./-]{3,100})['\"]", js)))
for u in urls:
    if re.search(r"wifi|wlan|net|ssid|config|setting|iface|mqtt|wlan", u, re.I):
        print("URL", u)
