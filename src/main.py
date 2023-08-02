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
        bucket_size = os.getenv("BUCKET_SIZE")
        bucket_size = int(bucket_size) if bucket_size is not None else 10
        central.run_central_cloud(port=port, bucket_size=bucket_size)
    else:
        central_url = f'http://{os.getenv("SERVER")}'
        threshold = os.getenv("THRESHOLD")
        threshold = int(threshold) if threshold is not None else 20
        port = int(port) if port is not None else 8001

        node.run_distributed_node(central_url,
                                  port=port,
                                  to_server_threshold=threshold,
                                  scan_frequency=threshold/5)


if __name__ == "__main__":
    main()
