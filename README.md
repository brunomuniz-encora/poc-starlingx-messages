# The very simple PoC of an app that sends message to a server

- [ ] Add some sort of simple retry logic for offline nodes

>_NOTE_: At the end of the session of the central node (when interrupted),
> a timeseries of the received data is generated.

## Running as a Demo

For a Demo, just do:

```shell
python3 -m venv venv; \
source venv/bin/activate; \
pip install -r requirements/requirements.txt; \
MODE=central ./src/app.py & \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done; \
sleep 5; \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done; \
sleep 5; \
for i in {1..5}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done; \
sleep 5; \
for i in {1..10}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done; \
sleep 5; \
for i in {1..30}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done; \
sleep 5; \
kill $(ps -ef | grep app.py | awk '{print $2}')
```

## Running locally

Run the central with:

```shell
MODE=central ./src/app.py
```

Run any number of nodes with something like:

```shell
for i in {1..2}; do MODE=node SERVER=127.0.0.1:8000 ./src/app.py &>/dev/null & done
```

Visit [localhost:8000](localhost:8000) on your browser to see 
all the messages received by the central.

Kill all when you're done with:

```shell
sudo kill $(ps -ef | grep app.py | awk '{print $2}')
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
docker run --network host -e MODE=node -e SERVER=127.0.0.1:8000 -it --rm poc-starlingx
```

## Docker build and Kubernetes run

> _NOTE_: I'm using a local registry for this

To build the dokcer image:

```shell
docker build -t poc-starlingx .
```

Tag and push the docker image:

```shell
docker tag poc-starlingx localhost:5000/poc-starlingx
docker push localhost:5000/poc-starlingx
```

WIP WIP WIP WIP WIP WIP WIP WIP WIP
