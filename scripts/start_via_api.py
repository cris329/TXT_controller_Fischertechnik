# -*- coding: utf-8 -*-
"""Start Futball workspace through permanent txtapi process.

Purpose: survive SSH/sudo session end; GUI shows Running.
Context: must run as ftgui (reads apikey). Never prints the key.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import urllib.error
import urllib.request

API = "http://127.0.0.1:8080/api/v1"
KEY_FILE = "/opt/ft/config/apikey"
NAME = "Futball"


def _key():
    """Read API key from controller config.

    @return: str
    """
    with open(KEY_FILE, "r") as fh:
        return fh.read().strip()


def _call(method, path):
    """HTTP call to txtapi with X-API-KEY.

    @param method: GET/POST/DELETE
    @param path: API path under /api/v1
    @return: (code, body)
    """
    data = b"" if method in ("POST", "PUT") else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("X-API-KEY", _key())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.getcode(), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        return exc.code, body
    except Exception as exc:
        return 0, str(exc)


def main():
    """Stop previous app then start Futball via txtapi.

    @return: None
    """
    code, body = _call("POST", "/application/%s/start" % NAME)
    print("start %s %s" % (code, body[:220].replace("\n", " ")))
    if code != 200:
        _call("DELETE", "/application/stop")
        code, body = _call("POST", "/application/%s/start" % NAME)
        print("retry %s %s" % (code, body[:220].replace("\n", " ")))


if __name__ == "__main__":
    main()
