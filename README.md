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

See [Demo](Demo.md) (10-minutes reading).

### Optional overrides

This application supports others overrides and variables.
The full available override can be seen bellow.

   ```shell
   env:
     - name: MODE
       value: <node/central>
     - name: SERVER
       value: <central IP address:port>
     - name: PORT
       value: <"container-port"> # Environment variable that determines which 
       # port the application will listen inside the container (note that the 
       # port value must be in double quotes)
     - name: BUCKET_SIZE
       value: <time-in-seconds> # Value that determines how many seconds the
       # central will accumulate data before it process them 
     - name: THRESHOLD
       value: <threshold> # Determines the threshold value in which the node
       # will notify the central if the generated value is above the threshold 

   image:
     repository: <local-or-remote-repository>
     tag: <tag>
     containerPort: <container-port> # Determines which port the kubernetes will
     # look for the application inside the container (must be the same as the 
     # environment variable above)

   kube:
     port: <system-port> # Determines which port will be exposed on the kubernetes cluster host
     replicas: <number-of-replicas>
     secret: <local-registry-secret>
     name: <kubernetes-deployment-name>
   ```
