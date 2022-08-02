#!/usr/bin/env python3

import json

proxy = {
        "dc1": [
            "10.4.10.200",
            "10.4.10.201",
            ],
        "dc2":[
            "10.2.16.200",
            "10.2.16.201",
            "10.2.16.202",
            ],
        }

proxy_list = []

for dc, ip_list in proxy.items():
    for ip in ip_list:
        proxy_list.extend(
            {
                "datacenter": dc,
                "admin_addr": f"{ip}:{11080 + i}",
                "proxy_addr": f"{ip}:{19000 + i}",
            }
            for i in [0, 2]
        )

with open("instance.json", 'w+') as f:
    f.write(json.dumps(proxy_list, indent=4))

for x in proxy:
    print(f"[{x}]:")
    proxy_addr = ""
    for p in proxy_list:
        if p["datacenter"] == x:
            if len(proxy_addr) != 0:
                proxy_addr += ","
            proxy_addr += p["proxy_addr"]
    print(proxy_addr)
    print("\n")

