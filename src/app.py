#!/usr/bin/env python3

import os

from src.app import central, node


def main():
    mode = os.getenv("MODE")
    print("mode -> " + mode)

    if mode == "central":
        central.run_central_server(handler_class=central.DefaultCentralRequestHandler)
    else:
        central_url = f'http://{os.getenv("SERVER")}'
        node.run_distributed_node(central_url)


if __name__ == "__main__":
    main()
