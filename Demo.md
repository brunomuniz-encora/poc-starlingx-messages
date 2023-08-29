# Poc-StarlingX

## Deploying PoC-StarlingX as a StarlingX Application

1. To deploy the PoC-StarlingX app as a StalingX Application, you first need to
package it. The `package-stx` `Make` target takes care of packaging the
application in the format expected by StarlingX:

    ```makefile
    VERSION := $(shell cat VERSION)
    
    CHART_NAME := $(shell cat helm-chart/Chart.yaml | grep name | awk -F ': ' '{print $$2}')
    CHART_VERSION := $(shell cat helm-chart/Chart.yaml | grep -E '^version' | awk -F ': ' '{print $$2}')
    
    package-helm:
        helm package helm-chart/
    
    package-plugin:
        cd stx-plugin; \
        python3 setup.py bdist_wheel \
        --universal -d k8sapp_poc_starlingx
        # clean up
        rm -r stx-plugin/build/ stx-plugin/k8sapp_poc_starlingx.egg-info/ stx-plugin/AUTHORS stx-plugin/ChangeLog
    
    package-stx: package-helm package-plugin
        mkdir -p stx-packaging/charts
        mkdir -p stx-packaging/plugins
        mv poc-starlingx*.tgz stx-packaging/charts/
        mv stx-plugin/k8sapp_poc_starlingx/k8sapp_poc_starlingx*.whl stx-packaging/plugins/
        cd stx-packaging; find . -type f ! -name '*.md5' -print0 | xargs -0 md5sum > checksum.md5
        cd stx-packaging; tar -czvf ../poc-starlingx-stx-pkg.tar.gz *
        # clean up
        rm stx-packaging/checksum.md5
        rm -r stx-packaging/charts/
        rm -r stx-packaging/plugins/
    ```
    
    [//]: # (TODO: Add video/gif of the `make package-stx` running)
    
    > _NOTE_: The format expected by StarlingX is explained in details in the 
    > [BuildGuide.md](BuildGuide.md).

2. After packaging the app, send the generated `poc-starlingx-stx-pkg.tar.gz`
file to the StarlingX controller(s) where you want the app(s) to run. Then you
can simply run:

    ```shell
    system application-upload /path/to/poc-starlingx-stx-pkg.tar.gz
    ```
    [//]: # (TODO: add video here)
3. This application works with two different personalities, controlled via
environment variables.
   1. If you are deploying the app with the `central` personality, simply run:
        ```shell
        system application-apply poc-starlingx
        ```
        [//]: # (TODO: add video here)
   2. If you are deploying the app with the `node` personality:
       1. generate a Helm overrides file called `node-overrides.yaml`:
       ```shell
       env:
         - name: MODE
           value: node
         - name: SERVER
           value: <central IP address>
       ```
       [//]: # (TODO: add video here)
       2. Apply the new override:
       ```shell
       system helm-override-update --values /path/to/node-overrides.yaml poc-starlingx poc-starlingx default
       ```
       [//]: # (TODO: add video here)
       3. Deploy the application with:
       ```shell
       system application-apply poc-starlingx
       ```
       [//]: # (TODO: add video here)

## Application Demo

The `central` is constantly receiving updates from `node`s, which can be seen
below by the timeseries graphs and the list of recently connected clients.

[//]: # (TODO Add screenshot here.)

The `node` is constantly generating new data that, if above a given threshold,
is sent to the `central`. Points above the red line in the timeseries below
represent the data that is sent to the `central`.

[//]: # (TODO Add screenshot here.)

When a `node` is, for any reason, not able to send data to the `central`, it
continues to generate data. When the `node` is able to contact the central again
, past data is sent. The `central` receives past data and process it accordingly
, showing in the timeseries the actual timestamps of the events as well as
another timeseries with the timestamp of when data is received, showing a burst
of events received when the `node` became available again.

## The whole process

The whole process of deploying and demoing the app can be seen in the video
below:

[//]: # (TODO Add complete video here.)
