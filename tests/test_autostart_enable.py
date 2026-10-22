# -*- coding: utf-8 -*-
"""Unit tests for Autostart Menu.conf rewriting logic."""

from __future__ import print_function

import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def _rewrite(text, load_path):
    """Apply same rewrite rules as autostart_enable.

    @param text: Menu.conf body
    @param load_path: absolute Futball.py path
    @return: rewritten text
    """
    lines = text.splitlines()
    out = []
    seen_load = False
    seen_start = False
    for line in lines:
        if line.startswith("fileAutoLoad="):
            out.append("fileAutoLoad=" + load_path)
            seen_load = True
        elif line.startswith("fileAutoStart="):
            out.append("fileAutoStart=true")
            seen_start = True
        else:
            out.append(line)
    if not seen_load:
        out.insert(1, "fileAutoLoad=" + load_path)
    if not seen_start:
        out.insert(2, "fileAutoStart=true")
    return "\n".join(out) + "\n"


def test_enables_autostart_existing_keys():
    """Happy path: existing keys are overwritten."""
    src = "[General]\nfileAutoLoad=\nfileAutoStart=false\nlanguage=es\n"
    out = _rewrite(src, "/opt/ft/workspaces/Futball/Futball.py")
    assert "fileAutoLoad=/opt/ft/workspaces/Futball/Futball.py" in out
    assert "fileAutoStart=true" in out
    assert "language=es" in out


def test_inserts_missing_keys():
    """Edge: missing keys are inserted under [General]."""
    src = "[General]\nlanguage=es\n"
    out = _rewrite(src, "/x/Futball.py")
    assert out.splitlines()[1].startswith("fileAutoLoad=")
    assert "fileAutoStart=true" in out


def test_does_not_drop_other_sections(tmp_path=None):
    """Error/regression: other sections remain intact."""
    src = "[General]\nfileAutoLoad=old\nfileAutoStart=false\n[WiFi]\nssid=home\n"
    out = _rewrite(src, "/opt/ft/workspaces/Futball/Futball.py")
    assert "[WiFi]" in out
    assert "ssid=home" in out
