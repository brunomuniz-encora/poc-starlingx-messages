# The very simple PoC of an app that sends message to another app

This is a very basic app that act as either a `central` or a `node`:

- `central`: receives messages; plots received messages and clients connected.
- `node`: generates random data (threats); sends a message to a `central` when
  threats are above a given threshold.

Take a look at the [Demo](Demo.md) (10-minutes reading).

You can also understand how a StarlingX Application is packaged in the
[BuildGuide](BuildGuide.md).
  
## Quick start

For a local Demo, simply do:

```shell
python3 -m venv venv; \
source venv/bin/activate; \
pip install -r requirements/requirements.txt; \
export PYTHONPATH=$(pwd)/src:$(pwd)/src/app; \
MODE=central BUCKET_SIZE=10 ./src/main.py & \
for i in $(seq 1 5); do MODE=node SERVER=127.0.0.1:8000 PORT=$((8000+$i)) ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in $(seq 6 10); do MODE=node SERVER=127.0.0.1:8000 PORT=$((8000+$i)) ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in $(seq 11 15); do MODE=node SERVER=127.0.0.1:8000 PORT=$((8000+$i)) ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in $(seq 16 30); do MODE=node SERVER=127.0.0.1:8000 PORT=$((8000+$i)) ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in $(seq 31 60); do MODE=node SERVER=127.0.0.1:8000 PORT=$((8000+$i)) ./src/main.py &>/dev/null & done;
```

You'll be able to see the `central` dashboard in
[http://localhost:8000](http://localhost:8000) and `node` dashboards on
subsequent ports (from 8001 to 8060 in this example).

Kill all after you're done (sorry if this kills another process of yours):

```shell
kill $(ps -ef | grep main.py | awk '{print $2}')
```

## Running locally

You can get hints about how to run things from the [Quick start](#quick-start)
above.

## Running in StarlingX

Overall steps (example):

- Run `make package-stx`: a `poc-starlingx-stx-pkg.tar.gz` file is created.
- Copy the file above to your StarlingX box: `scp ...`.
- Upload package with:
  ```shell
  system application-upload poc-starlingx-stx-pkg.tar.gz
  ```
- Optionally, generate a Helm overrides file, for example:
  ```shell
  env:
    - name: MODE
      value: server
  
  kube:
    port: 32100
    name: poc-starlingx # will affect names of pods
  ```
- Optionally, apply the new override:
  ```shell
  system helm-override-update poc-starlingx poc-starlingx default
  ```
- Deploy the application with:
  ```shell
  system application-apply poc-starlingx
  ```
