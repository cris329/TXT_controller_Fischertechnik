# -*- coding: utf-8 -*-
"""Stop running TXT application via txtapi."""
from __future__ import print_function
import urllib.error
import urllib.request

KEY_FILE = "/opt/ft/config/apikey"
API = "http://127.0.0.1:8080/api/v1/application/stop"


def main():
    """DELETE /application/stop.

    @return: None
    """
    key = open(KEY_FILE).read().strip()
    req = urllib.request.Request(API, data=b"", method="DELETE")
    req.add_header("X-API-KEY", key)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("stopped", resp.getcode())
    except urllib.error.HTTPError as exc:
        print("http", exc.code, exc.read()[:120])
    except Exception as exc:
        print("err", exc)


if __name__ == "__main__":
    main()
