#!/usr/bin/env python3

from utils import *

import atexit
import json
import datetime


class CodisSentinel(Process):

    def __init__(self, port):
        self.config = self._open_config(port)
        self.port = port

        self.logfile = f"sentinel-{port}.log"
        self.command = f"codis-server {self.config} --sentinel"
        Process.__init__(self, self.command, self.logfile)

        dict = {"port": port, "pid": self.proc.pid}
        print(f"    >> codis.sentinel = {json.dumps(dict, sort_keys=True)}")

    @staticmethod
    def _open_config(port):
        config = f'sentinel-{port}.conf'
        with open(config, "w+") as f:
            f.write(f'port {port}')
        return config


if __name__ == "__main__":
    children = []
    atexit.register(kill_all, children)

    children.extend(CodisSentinel(port) for port in range(26380, 26385))
    check_alive(children, 3)

    while True:
        print(datetime.datetime.now())
        time.sleep(5)
