# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/8/4
Description:
    win32_memurai_ctrl.py
----------------------------------------------------------------------------"""

import os
import psutil
import subprocess

MEMURAI_PATH = "./memurai/"


class MemuraiController(object):
    def __init__(self):
        self._pid = None

    def start(self):
        if self._pid:
            self.stop()

        p = subprocess.Popen(os.path.join(MEMURAI_PATH, "memurai.exe"))
        self._pid = p.pid

    def stop(self):
        if self._pid:
            try:
                if self._pid in [p.pid for p in psutil.process_iter()]:
                    p = psutil.Process(self._pid)
                    p.kill()
            except Exception as ex:
                print("MemuraiController stop exception: %s" % ex)
