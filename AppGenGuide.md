TODO: move to the App Generator repo after validation of these changes.

# Deploy an application as a StarlingX app

This guide describes the steps to deploy an application as a **StarlingX App** 
utilizing the StarlingX's App Generator tool.

If you want to learn more about the app generator tool, please visit
https://github.com/Danmcaires/StarlingX-App-Generator (this is a temporary
repository, all relevant info/code, if any, will be moved to official
repositories by the end of this study).

- [Prerequisites](#prerequisites)
- [Generate the application](#generate-the-application)
  - [App manifest configuration](#app-manifest-configuration)
  - [Metadata File Configuration](#metadata-file-configuration)
  - [App Setup configuration](#app-setup-configuration)
- [Run the application](#run-the-application)
  - [FluxCD Manifest](#fluxcd-manifest)
  - [Plugins](#plugins)
  - [Metadata](#metadata)
  - [Tarballs](#tarballs)
- [Customizing the application](#customizing-the-application)
  - [FluxCD Manifest](#fluxcd-manifest-1)
  - [Plugins](#plugins-1)
  - [Other files](#other-files)
  - [Packaging the application](#packaging-the-application)

## Prerequisites

As the StarlingX Platform manages a distributed Kubernetes cluster, for an
application to be deployed as a StarlingX App it needs to be designed so it can
run on [Kubernetes](https://kubernetes.io/).

Additionally, it needs to provide a [Helm Chart](https://helm.sh/)
which will be managed via [Flux](https://fluxcd.io/) by StarlingX itself.

## Generate the StarlingX Application package

Clone the app-generator repository.
```shell
git clone https://github.com/Danmcaires/StarlingX-App-Generator.git
```

This is what you'll find in the root folder of the repository:

> _NOTE_: TODO update image.

![file-structure](BuildGuide/file-strucuture-1.png)

The `app_manifest.yaml` is the most important configuration step since it
specifies everything necessary to build the StarlingX application.

The app manifest configuration can be divided into three parts, which will
have their own dedicated section below:

- [App manifest configuration](#app-manifest-configuration)
- [Metadata file configuration](#metadata-file-configuration)
- [App Setup Configuration](#app-setup-configuration)

### App manifest configuration

In this stage the section **appManifestFile-config** from the
`app_manifest.yaml` will be configured.

![app manifest config](BuildGuide/app-manifest-config-empty.png)

These are the minimum required fields that will need to be filled in order
for the StarlingX App Generator to work properly.

Below you will find a brief explanation of every one of the required fields
which will help you fill them out for you application:

- **appName** field: desired StarlingX application name, referenced throughout
the whole system.
- **appVersion** field: the version of the application that the generated
package will represent.
- **namespace** field: desired StarlingX application namespace (note that this
namespace is not the same as the Kubernetes namespace).
- **chart** section: an array with an object for every Helm chart in your
application. Each object contains:
  - **name** field: your Helm chart name as it is in the chart metadata.
  - **version** field: your chart version as it is in the chart metadata.
  - **path** field: relative path to the Helm chart directory, Helm repo or
  Helm package file. 
  > _NOTE_: Currently only Helm charts in directories have been tested.
  - **chartGroup** field: default is _application-name-charts_.
- **chartGroup** section:
  - **name**: only one chart group per application.
  - **chart_names**: a list of the names of the charts from your application.

### Metadata File Configuration

In this stage the section **metadataFile-config** from the
`app_manifest.yaml` will be configured.

This section's objective is to configure the generation/creation of a
`metadata.yaml` file, which is the core metadata file for a StarlingX App
package.

This `metadata.yaml` file is very flexible, hence the **metadataFile-config**
section is also very flexible. Other values may be passed in order to enable
advanced features within the StarlingX platform. For a better understanding of
each attribute in this section please refer to
[this link](https://wiki.openstack.org/wiki/StarlingX/Containers/StarlingXAppsInternals#metadata.yaml).

### App Setup configuration

In this stage the section **setupFile-config** from the `app_manifest.yaml`
will be configured.

Below you will find a brief explanation of every one of the required fields
which will help you fill them out for you application:

![setup cfg image](BuildGuide/setup-cfg.png)

- **metadata** section:
  - **author/author-email/url fields**: authorship information.
  - **classifier** section: TODO needs description of what this is.

This section is related to the `setup-cfg` file that will be generated. For
more advanced use cases you may want to refer to [the documentation](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html).

## Run the StarlingX App Generator

```shell
python3 app-gen.py -i app_manifest.yaml
```

With the command above, the StarlingX App Generator will create a set of files
and package everything in the StarlingX format.

The following sections explain in high-level the most important parts of the
package.

### FluxCD Manifest

The generator will first create the FluxCD Manifest following the structure below:

```shell
fluxcd-manifests/
├── base
│   ├── helmrepository.yaml
│   ├── kustomization.yaml
│   └── namespace.yaml
├── kustomization.yaml
└── CHART-NAME
    ├── helmrelease.yaml
    ├── kustomization.yaml
    ├── CHART-NAME-static-overrides.yaml
    └── CHART-NAME-system-overrides.yaml
```

For every Helm chart configured in the `app_manifest.yaml` file, a folder with
the name of the chart will be created. 

> **_NOTE_**: The `CHART-NAME-static-overrides.yaml` file will be empty.

### Plugins

After the creation of the FluxCD Manifest, the generator will also create a set
of plugins with an empty implementation.

The Structure of the plugins created will be:

```shell
plugins/
├── k8sapp_APP_NAME
│   ├── common
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── helm
│   │   ├── __init__.py
│   │   └── CHART_NAME.py
│   ├── kustomize
│   │   ├── __init__.py
│   │   └── kustomize_APP_NAME.py
│   └── lifecycle
│       ├── __init__.py
│       └── lifecycle_APP_NAME.py
├── __init__.py
├── setup.cfg
└── setup.py
```

The `setup.cfg` file will be created according to the
[`setupFile-config`](#app-setup-configuration) section in the `app_manifest.yaml`.

### Metadata

In the third step of the execution the `metadata.yaml` file will be generated
with the information given in [`metadataFile-config`](#metadata-file-configuration)
section in the `app_manifest.yaml`.

### Tarballs

After the main files have been created, the generator will start packaging
everything.

Firstly it will package every helm-chart, that was given in the 
`app_manifest.yaml` file, into a `.tgz` file, saving these files into a folder
named `charts`.

The generator, then, will package the plugins with the [wheel](https://peps.python.org/pep-0491/)
format.

Lastly, creates a checksum sha256 signature file for the output tarball and
the output tarball itself, which will be called

```
<APPNAME>-<APPVERSION>.tgz
```

The structure of the app inside the tarball will be the following:

```shell
 APPNAME-APPVERSION.tgz/
 ├── charts/
 ├── fluxcd-manifests/
 ├── plugins/
 ├── checksum.sha256
 └── metadata.yaml
```

> **Warning:**
> At this point, the generated package is a working StarlingX App, however it
> contains empty templates for some files. The following sections will describe
> how to further enhance your StarlingX App. 

## Customizing the application

If you wish to customize Flux and the plugins for the particularities of
your application, it is important to modify some of the generated files.

In order to allow such customization, the generator provides additional
functions to modify specific files in the package.

```shell
python3 app-gen.py -i app_manifest.yaml [-o ./output] [--overwrite] [--no-package]|[--package-only]
```

Where:

- `-i/--input`: path to the `app_manifest.yaml` configuration file.
- `-o/--output`: output folder. Defaults to a new folder with the app name in
the current directory.
- `--overwrite`: deletes existing output folder before starting.
- `--no-package`: only creates the FluxCD manifest, plugins and the
  metadata file, without compressing them in a tarball.
- `--package-only`: create the plugins wheels, sha256 file, helm-chart tarball
  and package the entire application into a tarball.

This means that, in order to be able to make additional configuration, one must:

- first run the App Generator with `--no-package`;
- then do the changes (described in the following sections);
- finally, run the App Generator again with `--package-only`.

### FluxCD Manifest

[//]: # (TODO: Validate this information - what needs validation?)

Most of the generated manifest won't need any modification, but for every 
helm-chart in the `app_manifest.yaml`, a static overrides file will be created.
The static overrides contain all information that is not to be overwritten
inside the values.yaml of the helm-chart.

### Plugins

The generate will create 3 main plugins, the helm, the kustomize and the lifecycle.

- The `helm/APP_NAME.py` file is responsible for the overriding methods that will
  be used to create the Helm overrides for the StarlingX App.

- The `kustomize_APP_NAME.py` is a plugin that is used to make changes to the
  top-level kustomization resource list based on the platform mode.

- The `lifecycle_APP_NAME.py` is responsible for performing lifecycle actions on the
  application using the lifecycle hooks of the StarlingX Platform.

The files created by the generator will have empty implementations and is up to
the developer to implement everything that is necessary for the application to
run as intended.

The `sysinv` folder in the [StarlingX config repository](https://opendev.org/starlingx/config/src/branch/master/sysinv/sysinv/sysinv/sysinv) contains a multitude of functions and variables that may be
helpful in the development of application plugins.

### Other files

For the customization of the application the modifications above, in the FluxCD
and the plugins, should be enough for the application to run as expected in the
StarlingX platform.

With that in mind, it is recommended to check if the `metadata` and the `setup.cfg`
have been created as they should. Particularly, the `setup.cfg` may need careful
attention if the modifications on the plugin file should be reflected in it.
