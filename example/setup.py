#!/usr/bin/env python3

from server import *
from sentinel import *
from dashboard import *
from proxy import *
from fe import *


def codis_admin_dashboard(admin_port, args=None):
    command = f"codis-admin --dashboard 127.0.0.1:{admin_port}"
    if args is not None:
        command += f" {args}"
    return do_command(command)


def codis_admin_proxy(admin_port, args=None):
    command = f"codis-admin --proxy 127.0.0.1:{admin_port}"
    if args is not None:
        command += f" {args}"
    return do_command(command)

if __name__ == "__main__":
    children = []
    atexit.register(kill_all, children)

    product_name = "demo-test"
    product_auth = None

    # step 1. codis-server & codis-sentinel

    # codis-server [master 2000+i <== following == 3000+i slave]
    for i in range(4):
        children.append(CodisServer(2000 + i, requirepass=product_auth))
        children.append(CodisServer(3000 + i, 2000 + i, requirepass=product_auth))

    children.extend(CodisSentinel(20000 + i) for i in range(5))
    check_alive(children, 1)
    print("[OK] setup codis-server & codis-sentinel")

    # step 2. setup codis-fe & codis-dashboard & codis-proxy

    children.append(CodisFE(8080, "../cmd/fe/assets"))
    children.append(CodisDashboard(18080, product_name, product_auth))

    children.extend(
        CodisProxy(11080 + i, 19000 + i, product_name, product_auth)
        for i in range(4)
    )

    check_alive(children, 3)
    print("[OK] setup codis-fe & codis-dashboard & codis-proxy")

    # step3: init slot-mappings

    for i in range(4):
        gid = i + 1
        codis_admin_dashboard(18080, f"--create-group --gid={gid}")
        codis_admin_dashboard(
            18080,
            f"--group-add --gid={gid} --addr=127.0.0.1:{2000 + i} --datacenter=localhost",
        )

        codis_admin_dashboard(
            18080,
            f"--group-add --gid={gid} --addr=127.0.0.1:{3000 + i} --datacenter=localhost",
        )

        beg, end = i * 256, (i + 1) * 256 - 1
        codis_admin_dashboard(
            18080,
            f"--slots-assign --beg={beg} --end={end} --gid={gid} --confirm",
        )

        codis_admin_dashboard(18080, f"--resync-group --gid={gid}")

    for i in range(5):
        codis_admin_dashboard(18080, f"--sentinel-add --addr=127.0.0.1:{20000 + i}")

    codis_admin_dashboard(18080, "--slot-action --interval=0")
    codis_admin_dashboard(18080, "--sentinel-resync")

    check_alive(children, 3)
    print("[OK] done & have fun!!!")

    while True:
        print(datetime.datetime.now())
        time.sleep(5)
