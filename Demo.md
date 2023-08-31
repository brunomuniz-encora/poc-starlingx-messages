# Poc-StarlingX

This is an application developed as a proof of concept for the StarlingX
Platform.

The application simulates a network of anti-virus scanners running independently
and geographically monitoring for threats. When the scan detects threats above 
a threshold it reports to a central instance responsible for receiving all the 
reports, process and store them, and output the information in a time series graph. 

The application works as a system that either generates information or receives
information from another instance of the application. This is understood as
the application having two different personalities, the `node` which is the one
that generates the information, and the `central` that receives the messages.


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
    
   ![make package-stx gif](README/make-pkg.gif)
    
   > _NOTE_: The format expected by StarlingX is explained in details in the 
   > [BuildGuide.md](BuildGuide.md).

2. After packaging the app, send the generated `poc-starlingx-stx-pkg.tar.gz`
file to the StarlingX active controller(s) where you want the app(s) to run. Then you
can simply run:
   
   ```shell
   source /etc/platform/openrc; system application-upload /path/to/poc-starlingx-stx-pkg.tar.gz
   ```
   ![upload package-stx gif](README/upload-pkg.gif)
3. This application has two different personalities, controlled via
environment variables.
   1. If you are deploying the app with the `central` personality, simply run:
      ```shell
      source /etc/platform/openrc; system application-apply poc-starlingx
      ```
      ![apply app gif](README/apply-app.gif)
   2. If you are deploying the app with the `node` personality:
      1. generate a Helm overrides file called `node-overrides.yaml`:
      ```shell
      env:
        - name: MODE
          value: node
        - name: SERVER
          value: <central IP address:port>
      ```
      2. Apply the new override:
      ```shell
      source /etc/platform/openrc; system helm-override-update --values /path/to/node-overrides.yaml poc-starlingx poc-starlingx default
      ```
      3. Deploy the application with:
      ```shell
      source /etc/platform/openrc; system application-apply poc-starlingx
      ```
      ![apply node gif](README/apply-node.gif)


## Application Demo

[//]: # (TODO this whole text needs proofreading)

Below you are seeing a `central` running on the right side of the screen and 4
`node`s running on the left side. `Node`s 1 and 2, on the top, are running with
a threshold of 5%, which means they are more sensitive, notifying the `central`
more frequently. `Node`s 3 and 4 at the bottom are running with a threshold of
20%.

The `central` (to the right) presents the following information:

- a timeseries of the processed events (based on the timestamp when the event
was created on the `node`);
- a constantly updated list of recently connected `nodes`;
- a timeseries of received events (based on `central`'s timestamp when the event
was received).

All 4 `node`s, to the left, are constantly generating new data which, if above
the configured threshold for the `node`, is sent to the `central`. Points above
the red line in the timeseries represent the data from each node that is sent to
the `central`.

[//]: # (TODO Add screenshot of the whole thing here.)

When a `node` is, for any reason, not able to send data to the `central`, it
continues to generate and accumulate data. 

> _NOTE_: This offline status can be simulated with the click of a button in
this demonstration.

[//]: # (TODO: turning nodes offilne and showing how it reflects on the timeseries)

Notice how the number of reported events has gone down from around X to Y.

[//]: # (TODO: update X and Y accoding to recording)

When the `node` is able to reach the central again, accumulated data on the node
is then sent to the `central`.

[//]: # (TODO turn nodes online again and show how it reflects on both central's graphs)

Processing of the new data by the `central` is shown as a spike of events
received (second graph on the `central`'s admin page). The events data, on the
other hand, are reprocessed and the first graph is updated accordingly.

## The whole process

The whole process of deploying and demoing the app can be seen in the video
below:

[//]: # (TODO Add complete video here.)
