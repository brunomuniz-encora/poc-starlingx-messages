# The very simple PoC of an app that sends message to a server

- [X] Generate timeseries on demand
- [ ] Node ID should be assigned be server
- [ ] Add some sort of simple retry logic for offline nodes

>_NOTE_: At the end of the session of the central node (when interrupted),
> a timeseries of the received data is generated.

## Running as a Demo

For a Demo, just do:

```shell
python3 -m venv venv; \
source venv/bin/activate; \
pip install -r requirements/requirements.txt; \
MODE=central ./src/main.py & \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in {1..10}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done; \
sleep 5; \
for i in {1..30}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done; \
sleep 5; \
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

Run any number of nodes with something like:

```shell
for i in {1..10}; do MODE=node SERVER=127.0.0.1:8000 ./src/main.py &>/dev/null & done
```

Visit [localhost:8000](localhost:8000) on your browser to see 
all the messages received by the central.

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
