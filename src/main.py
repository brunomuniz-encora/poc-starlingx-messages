#!/usr/bin/env python3

import os
import central
import node


def main():
    mode = os.getenv("MODE")
    port = os.getenv("PORT")
    print("mode -> " + mode)

    if mode == "central":
        port = int(port) if port is not None else 8000
        central.run_central_cloud(port=port)
    else:
        central_url = f'http://{os.getenv("SERVER")}'
        treshold = os.getenv("TRESHOLD")
        treshold = int(treshold) if treshold is not None else 20
        port = int(port) if port is not None else 8001

        node.run_distributed_node(central_url, port=port, to_server_treshold=treshold)


if __name__ == "__main__":
    main()
