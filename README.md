# The very simple PoC of an app that sends message to a server

- [X] Generate timeseries on demand
- [X] Central is able to receive past events from nodes and plot properly
- [ ] Add some sort of simple retry logic for offline nodes
- [X] Remove built charts from the helm-charts

>_NOTE_: At the end of the session of the central node (when interrupted),
> a timeseries of the received data is generated.

## Running as a Demo

For a Demo, just do:

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

## Docker build and run

To build the dokcer image:

```shell
docker build -t poc-starlingx .
```

Run an ephemeral container with the central with:

```shell
docker run -e MODE=central -p 8000:8000 -it --rm poc-starlingx
```

Run ephemeral nodes with:

```shell
docker run --network host -v /tmp/timeseries:/app/output \
-e MODE=node -e SERVER=127.0.0.1:8000 \
-it --rm poc-starlingx
```

## Helm

To build the chart:

```shell
mkdir charts
cd charts
helm package ../helm-chart/
```

### To run the `central`

Create the following file:

```shell
cat <<EOF > central.yaml
env:
  - name: MODE
    value: central

image:
  repository: <optional-registry-address>/poc-starlingx

fullNameOverride: poc-starlingx-central
EOF
```

Then run:

```shell
helm upgrade -i poc-starlingx-central poc-starlingx-0.4.0.tgz -f central.yaml
```

### To run a `node`

Create the following file:

```shell
cat <<EOF > node.yaml
env:
  - name: MODE
    value: node
  - name: SERVER
    value: <probably localhost:8000>

image:
  repository: <optional-registry-address>/poc-starlingx

fullNameOverride: poc-starlingx-central
EOF
```

Then run:

```shell
helm upgrade -i poc-starlingx-node poc-starlingx-0.4.0.tgz -f node.yaml
```

