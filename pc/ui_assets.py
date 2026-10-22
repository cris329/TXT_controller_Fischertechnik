# -*- coding: utf-8 -*-
"""Utilidades de assets del panel web.

Purpose: stamp de versión para CSS/JS.
Context: Flask dashboard en pc/app.py.
@author Cristian Deysdayr Jimenez
@created 2026-10-15
"""

import time


def asset_stamp():
    """Marca de tiempo para CSS/JS. @return: str"""
    return str(int(time.time()))
