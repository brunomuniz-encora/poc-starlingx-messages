# The very simple PoC of an app that sends message to a server

- [X] Generate timeseries on demand
- [X] Central is able to receive past events from nodes and plot properly
- [X] Add some sort of simple retry logic for offline nodes
- [X] Remove built charts from the helm-charts
- [X] Package as a Debian package
- [ ] FluxCD structure/packaging

>_NOTE_: At the end of the session of the central node (when interrupted),
> a timeseries of the received data is generated.

## Running as a Demo

For a local Demo, just do:

```shell
python3 -m venv venv; \
source venv/bin/activate; \
pip install -r requirements/requirements.txt; \
export PYTHONPATH=$(pwd)/src:$(pwd)/src/app; \
MODE=central BUCKET_SIZE=5 ./src/main.py & \
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

Kill all after you're done:

```shell
kill $(ps -ef | grep main.py | awk '{print $2}')
```

## Running locally

Setup:

```shell
python3 -m venv venv
pip install --upgrade pip
pip install -r requirements/dev.txt
```

Set up the nightmare `PYTHONPATH`:

```shell
export PYTHONPATH=$(pwd)/src:$(pwd)/src/app
```

Run the central with:

```shell
MODE=central ./src/main.py
```  

Run a node with something like:

```shell
MODE=node SERVER=127.0.0.1:8000 THRESHOLD=20 PORT=8001 ./src/main.py
```

You can lower the threshold to get more warnings:

```shell
MODE=node SERVER=127.0.0.1:8000 THRESHOLD=5 PORT=8002 ./src/main.py
```

Visit [localhost:8000](localhost:8000) on your browser to see 
all the messages received by the central.

Visit the nodes page at:

- [localhost:8001](localhost:8001) for the first node;
- [localhost:8002](localhost:8002) for the second node;
- and so on...

Kill all when you're done with:

```shell
sudo kill $(ps -ef | grep main.py | awk '{print $2}')
```

## Debian packaging

To package as a Debian package, run:

```shell
make package-debian
```

This creates a `.deb` file that you can install with:

```shell
sudo dpkg -i <.deb file>
```

You can later uninstall with:

```shell
sudo apt remove poc-starlingx
```

## Helm

To build the chart:

```shell
make package-helm
```

### To run the `central`

You can get an example override file in `packaging/helm/overrides/central-overrides.yaml`. Then run:

```shell
helm upgrade -i poc-starlingx-central poc-starlingx-0.4.0.tgz -f packaging/helm/overrides/central-overrides.yaml
```

### To run a `node`

You can get an example override file in `packaging/helm/overrides/node-overrides.yaml`. Then run:

```shell
helm upgrade -i poc-starlingx-central poc-starlingx-0.4.0.tgz -f packaging/helm/overrides/node-overrides.yaml
```
