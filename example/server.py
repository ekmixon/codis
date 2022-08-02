#!/usr/bin/env python3

from utils import *

import atexit
import json
import datetime


class CodisServer(Process):

    def __init__(self, port, master_port=None, requirepass=None):
        self.config = self._open_config(port, master_port, requirepass)
        self.port = port

        self.logfile = f"redis-{port}.log"
        self.command = f"codis-server {self.config}"
        Process.__init__(self, self.command, self.logfile)

        dict = {"port": port, "pid": self.proc.pid}
        print(f"    >> codis.server = {json.dumps(dict, sort_keys=True)}")

    @staticmethod
    def _open_config(port, master_port=None, requirepass=None):
        config = f'redis-{port}.conf'
        with open(config, "w+") as f:
            f.write(f'port {port}\n')
            f.write('save ""\n')
            f.write(f'dbfilename "{port}.rdb"\n')
            if master_port is not None:
                f.write(f'slaveof 127.0.0.1 {master_port}\n')
            if requirepass is not None:
                f.write(f'masterauth {requirepass}\n')
                f.write(f'requirepass {requirepass}\n')
            f.write('protected-mode no\n')
        return config


if __name__ == "__main__":
    children = []
    atexit.register(kill_all, children)

    passwd = None

    for port in range(16380, 16384):
        children.append(CodisServer(port, requirepass=passwd))
        children.append(CodisServer(port + 1000, port, requirepass=passwd))

    check_alive(children, 3)

    while True:
        print(datetime.datetime.now())
        time.sleep(5)
