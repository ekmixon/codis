#!/usr/bin/env python3

from utils import *

import atexit
import json
import datetime


class CodisDashboard(Process):

    def __init__(self, admin_port, product_name, product_auth=None):
        self.config = self._open_config(admin_port, product_name, product_auth)
        self.admin_port = admin_port
        self.product_name = product_name
        self.product_auth = product_auth

        self.logfile = f"dashboard-{admin_port}.log"
        self.command = f"codis-dashboard -c {self.config}"
        Process.__init__(self, self.command, self.logfile)

        dict = {"admin_port": admin_port, "pid": self.proc.pid}
        print(f"    >> codis.dashboard = {json.dumps(dict, sort_keys=True)}")

    @staticmethod
    def _open_config(admin_port, product_name, product_auth=None):
        config = f'dashboard-{admin_port}.toml'
        with open(config, "w+") as f:
            f.write('coordinator_name = "filesystem"\n')
            f.write('coordinator_addr = "rootfs"\n')
            f.write(f'product_name = "{product_name}"\n')
            if product_auth is not None:
                f.write(f'product_auth = "{product_auth}"\n')
            f.write(f'admin_addr = ":{admin_port}"\n')
            f.write('migration_method = "semi-async"\n')
            f.write('migration_async_maxbulks = 200\n')
            f.write('migration_async_maxbytes = "32mb"\n')
            f.write('migration_async_numkeys = 100\n')
            f.write('migration_timeout = "30s"\n')
            f.write('sentinel_quorum = 2\n')
            f.write('sentinel_parallel_syncs = 1\n')
            f.write('sentinel_down_after = "5s"\n')
            f.write('sentinel_failover_timeout = "10m"\n')
            path = os.getcwd()
            f.write(
                f'sentinel_notification_script = "{os.path.join(path, "sentinel_notify.sh")}"\n'
            )

            f.write(
                f'sentinel_client_reconfig_script = "{os.path.join(path, "sentinel_reconfig.sh")}"\n'
            )

        return config


if __name__ == "__main__":
    children = []
    atexit.register(kill_all, children)

    product_name = "demo-test"
    product_auth = None

    children.append(CodisDashboard(18080, product_name, product_auth))

    check_alive(children, 3)

    while True:
        print(datetime.datetime.now())
        time.sleep(5)
