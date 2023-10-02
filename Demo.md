# Deploying your application to StarlingX

Deploying your own application to StarlingX is as easy as any other Kubernetes
deployment out there. In this blog post we'll show you the process with a 
simple demonstration application.

It's important to understand an application can be deployed in many ways to
the Kubernetes cluster(s) that StarlingX manages:

- [raw Kubernetes](https://kubernetes.io/docs/tutorials/kubernetes-basics/deploy-app/deploy-intro/);
- [Helm](https://helm.sh/docs/intro/using_helm/#helm-install-installing-a-package);
- [Flux](https://fluxcd.io/); and finally
- StarlingX Application, which benefits from tight integration with the
  [StarlingX system](https://opendev.org/starlingx/config).

> _NOTE_: TODO Saying that Helm is the most popular package manager needs a reference/link.

In this particular demonstration we will focus on [Helm](https://helm.sh/),
which is the most popular package manager for Kubernetes. Future blog posts
will address other deployment types and their advantages.

Any developer that already packages their application with
[Helm](https://helm.sh/) will be able to deploy their application in
StarlingX without any hassle.

## The Demo App

The application simulates a network of antivirus scanners and threat-monitoring
running independently and geographically distributed called `nodes`. When a node
detects threats above a configurable threshold in an area it reports to a
`central` instance responsible for aggregating, processing, and storing data
from all the `nodes` while presenting a bird's-eye view in a simple dashboard.

The application can act either as a `node` or a `central` (which are called
"personalities") depending on the environment variables it has available.

- `Nodes` are geographically spread out doing the actual work of monitoring, for
example, local networks.
- `Central` is a deployment that receives messages from `nodes`, processing and
presenting data related to them.

It's also possible to configure the threshold of a `node`, which determines
their sensitivity in the scanner for threats.

## Deploying the Demo App

### Via a Helm Package

> _NOTE_: TODO this is a WIP section

### Via a Helm Repository

> _NOTE_: TODO this is a WIP section

## Deploying PoC-StarlingX as a StarlingX App

1. After [packaging the app](https://github.com/Danmcaires/StarlingX-App-Generator#deploy-an-application-as-a-starlingx-app)
, send the generated `poc-starlingx-stx-pkg.tar.gz` file to the StarlingX active controller(s)
where you want the app(s) to run. Then you can simply run:
   ```shell
   source /etc/platform/openrc; system application-upload /path/to/poc-starlingx-stx-pkg.tar.gz
   ```

   ![upload package-stx gif](README/upload-pkg.gif)

2. This application has two different personalities, controlled via
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

Below you see a `central` running on the right side of the screen and 4
`node`s running on the left side. `Node`s 1 and 2, on the top, are running with
a threshold of 5%, which means they are more sensitive, notifying the `central`
more frequently. `Node`s 3 and 4 at the bottom are running with a threshold of
20%.

The `central` (to the right) presents the following information:

- a time series of the processed events (based on the timestamp when the event
was created on the `node`);
- a constantly updated list of recently connected `nodes`;
- a time series of received events (based on `central`'s timestamp when the event
was received).

All 4 `node`s, to the left, are constantly generating new data. This random data
is generated using a long tail distribution and, if above a configured threshold
for the `node`, the data is sent to the `central`. Points above the red line in
the time series represent the data from each node that is sent to the `central`.

![Demo overview](README/demo_overview.png)

When a `node` is, for any reason, not able to send data to the `central`, it
continues to generate and accumulate data.

> _NOTE_: This offline status can be simulated with the click of a button in
this demonstration.

![Turn nodes offline](README/app-demo-part-turn-offline.gif)

Notice how the number of reported events has gone down from around 12 to 2 and
the aggregated Threat Index went from around 11 to 8 during the time that
`node`s 1 and 2 were offline.

When the `node`s can reach the `central` again, accumulated data
is then sent to the `central`.

![Turn nodes online](README/app-demo-part-turn-online.gif)

The `central` takes its time processing the recent burst of data and:

- updates its first graph to reflect the new data received by the `node`s;
- shows a spike of events received on the second graph.

## The whole process

Installing StarlingX (automated script):

[![Complete install](README/install_thumb.png)](https://www.youtube.com/watch?v=6z7EV17Emcw)

Deploying and demonstration:

[![Complete install](README/demo_thumb.png)](https://youtu.be/IvBomQANXlo)
