# Deploy an application as a StarlingX app

This guide describes the steps to deploy an application as a **StarlingX App**.

- [Deploy an application as a StarlingX app](#deploy-an-application-as-a-starlingx-app)
  - [Prerequisites](#prerequisites)
  - [Generate the application](#generate-the-application)
    - [App manifest configuration](#app-manifest-configuration)
    - [Metadata File Configuration](#metadata-file-configuration)
    - [App Setup configuration](#app-setup-configuration)
  - [Plugins](#plugins)
  - [Packaging the application](#packaging-the-application)

## Prerequisites

As the StarlingX Platform manages a distributed Kubernetes cluster, for an
application to be deployed as a StarlingX App it needs to be designed so it can
run on [Kubernetes](https://kubernetes.io/).

Additionally, it needs to provide a [Helm Chart](https://helm.sh/) which will be managed
via [Flux](https://fluxcd.io/).

## Generate the application
1. Clone the app-generator repository
   ```shell
   git clone https://github.com/Danmcaires/StarlingX-App-Generator.git
   ```
   please note that the repository following structure will be:
   
   ![file-structure](BuildGuide/file-strucuture-1.png)
2. Then copy your application helm-chart folders to the helm-chart app-generator directory, for the messages poc, the helm-chart directory is already in the expected place.
3. Create a copy of the ```app_manifest.yaml``` file for redundancy in case you want to look at It without modifications
4. Now we'll configure the ```app_manifest.yaml```, and this is the most important configuration step, since It's the only file You'll need to modify in order to build your app. We'll divide the app manifest configuration in three steps:
    1. App manifest configuration
    2. App Metadata Configuration
    3. App Setup Configuration

### App manifest configuration

5. In this stage will configure the fields inside the **appManifestFile-config**
   
   ![app manifest config](BuildGuide/app-manifest-config-empty.png)

   These are the minimum required fields that you'll need to fill in order to the app-generator work properly.

   Brief fields explanation:
   - **appName**: desired StarlingX application name
   - **appVersion**: desired StarlingX application name
   - **namespace**: desired StarlingX application namespace (note that this namespace is not the same as the kubernetes namespace)
   - **chart**: create a copy of name,version,path and chartGroup for every chart in your application
     - **name**: your helm-chart name as It is in the chart metadata
     - **version**: your app version as It is in the chart metadata
     - **path**: helm-chart directory, helm repo or helm tgz path. Currently we only tested with the helm-chart directory
     - **chartGroup**: default is _application_name-charts_
   - **chartGroup**
     - **name**: usually only one chart group name per application
     - **chart_names**: a list of the charts name from your application

### Metadata File Configuration

6. In this part of the file, you must configure the application ```metadata.yaml``` files. The app generator automatically creates the _app_name_ and _app_version_ fields from the values you put **appManifestFile-config** above. Other values may be passed, if you wish to learn more about other configurations please look at this [link](https://wiki.openstack.org/wiki/StarlingX/Containers/StarlingXAppsInternals#metadata.yaml)

### App Setup configuration

7. As in the [app manifest config](#app-manifest-configuration), fill the required fields ![setup cfg image](BuildGuide/setup-cfg.png).

- **classifier**: Please see the ```app_manifest_example.yaml``` to have an idea of this configuration. Change the minimum that makes sense to you.
- **other values**: If you're a more advanced stx user and need to set other configurations, just create other tags and if you need, please consult [this](https://opendev.org/starlingx/app-dell-storage/src/branch/master/python3-k8sapp-dell-storage/k8sapp_dell_storage/setup.cfg) for more examples and [this](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html) documentation page for other options.

## Plugins

To-do Daniel

An overall suggested structure for the `plugins` folder is as follows:

```shell
python3-k8sapp-APP-NAME/
├── k8sapp_APP_NAME
│   ├── common
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── helm
│   │   ├── __init__.py
│   │   └── APP_NAME.py
│   ├── kustomize
│   │   ├── __init__.py
│   │   └── kustomize_APP_NAME.py
│   ├── lifecycle
│   │   ├── __init__.py
│   │   └── lifecycle_APP_NAME.py
│   └── tests
│       ├──__init__.py
│       └── test.py
├── __init__.py
├── setup.cfg
└── setup.py
```

For a better understanding of each of the attributes in this yaml file refer to
[this link](https://wiki.openstack.org/wiki/StarlingX/Containers/StarlingXAppsInternals#metadata.yaml)
in order to determine the necessary attributes for your application.

## Packaging the application

Run the following command to generate the application package.tgz

```shell
python3 app-gen.py -i app_manifest.yaml
```