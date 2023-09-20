# Deploy an application as a StarlingX app

This guide describes the steps to deploy an application as a **StarlingX App** 
utilizing the app generator tool.

If you want to learn more about the app generator tool, please visit Its
[repository](https://github.com/Danmcaires/StarlingX-App-Generator)

- [Deploy an application as a StarlingX app](#deploy-an-application-as-a-starlingx-app)
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
which will be managed via [Flux](https://fluxcd.io/).

## Generate the application

1. Clone the app-generator repository
  
   ```shell
   git clone https://github.com/Danmcaires/StarlingX-App-Generator.git
   ```

   please note that the repository structure will be:

    ![file-structure](BuildGuide/file-strucuture-1.png)

2. Then copy the application helm-chart folders to the helm-chart app-generator directory, for the messages poc, the helm-chart directory is already in the expected place.

3. Create a copy of the ```app_manifest.yaml``` file for redundancy in case becomes necessary to look at it without modifications

4. Now the ```app_manifest.yaml``` needs to be configured, and this is the most important configuration step since it's the only file that will be needed to build the application. The app manifest configuration can be divided into three steps:
    1. App manifest configuration
    2. App Metadata Configuration
    3. App Setup Configuration

### App manifest configuration

5. In this stage the fields inside the **appManifestFile-config** will be configured

   ![app manifest config](BuildGuide/app-manifest-config-empty.png)

   These are the minimum required fields that will need to be filled in order for the app-generator to work properly.

   Brief fields explanation:
   - **appName**: desired StarlingX application name
   - **appVersion**: desired StarlingX application version
   - **namespace**: desired StarlingX application namespace (note that this namespace is not the same as the Kubernetes namespace)
   - **chart**: create a copy of name, version, path and chartGroup for every helm-chart in your application
     - **name**: your helm-chart name as it is in the chart metadata
     - **version**: your app version as it is in the chart metadata
     - **path**: helm-chart directory, helm repo or helm tgz path. Currently we only tested with the helm-chart directory
     - **chartGroup**: default is _application-name-charts_
   - **chartGroup**
     - **name**: Only one chart group per application
     - **chart_names**: a list of the names of the charts from your application

### Metadata File Configuration

6. In this part of the file, the application ```metadata.yaml``` file will be configured. The app generator automatically creates the _app_name_ and _app_version_ fields from the values put in the **appManifestFile-config** above. Other values may be passed in order to enable some features within the StarlingX  platform. For a better understanding of each of the attributes in this yaml file please refer to [this link](https://wiki.openstack.org/wiki/StarlingX/Containers/StarlingXAppsInternals#metadata.yaml)
in order to determine the necessary attributes for the application.

### App Setup configuration

7. As in the [app manifest configuration](#app-manifest-configuration), fill the required fields

    ![setup cfg image](BuildGuide/setup-cfg.png)

- **author/author-email/url**: Provide de information about the author or team.
- **classifier**: Please see the ```app_manifest_example.yaml``` to have an idea of this configuration. it must contain *Verificar com o Bruno*
- **other values**: If you're a more advanced stx user and need to set other configurations, just create other tags and if you need to, please consult [this](https://opendev.org/starlingx/app-dell-storage/src/branch/master/python3-k8sapp-dell-storage/k8sapp_dell_storage/setup.cfg) for more examples and [this](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html) documentation page for other options.

## Run the application

With the app_manifest.yaml configured it is expected to look approximately like the following:


```
appManifestFile-config:
  appName: stx-app
  appVersion: 1.0.1
  namespace: default
  chart:
    - name: chart1
      version: 1.0.1
      path: /path/to/chart1
      chartGroup: chartgroup1
  chartGroup:
    - name: chartgroup1
      chart_names:
        - chart1

metadataFile-config:
  upgrades:
    auto_update: no 
  maintain_attributes: true
  maintain_user_overrides: true

setupFile-config:
  metadata: 
      author: John Doe
      author-email: john.doe@email.com
      url: johndoe.com
      classifier: # required
        - "Operating System :: OS Independent"
        - "License :: OSI Approved :: MIT License"
        - "Programming Language :: Python :: 3"
```

For the generator to be completed run and generate all files, simply run

```shell
python3 app-gen.py -i app_manifest.yaml
```

The generator will create a set of files and package everything in a format that
the StarlingX platform will be able to interpret.

### FluxCD Manifest

The generator will first create the FluxCD Manifest following the structure bellow:

```
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

For every helm-chart passed in the ``app_manifest.yaml`` a folder with the name
of the chart wil created containing the above files. 

> **_NOTE_**: The ``CHART-NAME-static-overrides.yaml`` file will be empty.

### Plugins

After the creation of the FluxCD Manifest, the generator will also create a set
of plugins with an empty implementation.

The Structure of the plugins created will be:

```
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

The ``setup.cfg`` file will be created following the information given in 
`setupFile-config` in the ``app_manifest.yaml``.

### Metadata

In the third step of the execution the ``metadata.yaml`` will be generated
with the information given in `metadataFile-config` in the ``app_manifest.yaml``.

### Tarballs

After the main files have been created, the generator will start packaging everything.

1. Firstly it will package every helm-chart, that was given in the `app_manifest`,
into a ``.tgz`` file. Then it will save these files into a folder named charts.

2. The generator, then, will package the plugins into a wheel format.

3. Lastly it will generate a checksum sha256 file with the files that will be
inside the application tarball.

4. After all the files have been created, the generator will finally package everything
into a tarball with the following naming

    > APPNAME-APPVERSION.tgz

The structure of the app inside the tarball will be as follows

```shell
 APPNAME-APPVERSION.tgz/
 ├── charts/
 ├── fluxcd-manifests/
 ├── plugins/
 ├── checksum.sha256
 └── metadata.yaml
```

> **Warning:**
> When the generator run from the beginning to the end, the final app  tarball will
> contain every file that the StarlingX platform requires from an application.
> However it is essential to notice that the files that will configure the application
> will empty, making a generic set of files with little customization.

## Customizing the application

If you wish to customize the Flux and the plugins for the particularities of
the application, it is important to modify some of the generated files.

In order to allow such customization, the generator allows the user to decide
whether to execute the entire generator or only create the files to be modified
to be packaged later.

The entire set of options for calling the generator is

`$ python3 app-gen.py -i app_manifest.yaml [-o ./output] [--overwrite] [--no-package] [--package-only]`

Where:

- ``-i/--input`` Input app_manifest.yaml file
- ``-o/--output`` Output folder, if none is passed the generator will create a folder
  with the app name in the current directory.
- ``--overwrite`` Delete existing folder with the same name as the app name
- ``--no-package`` Only creates the fluxcd manifest, the plugins and the
  metadata file
- ``--package-only`` Create the plugins wheels, sha256 file, helm-chart tarball
  and package the entire application into a tarball.

In order to be able to modify the plugins and overrides before packaging the 
application the user will need to use `--no-package` in the python call. By using
this option the generator will:

- Generate the FluxCD Manifest;
- Generate the plugins with an empty implementation;
- Generate the metadata.yaml
  
After creating the above files, the app generator will end its execution.

### FluxCD Manifest

[//]: # (TODO: Validate this information)

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

The files created by the generator will have empty implementations and are up to
the developer to implement everything that is necessary for the application to
run as intended.

The `sysinv` folder in the [StarlingX config repository](https://opendev.org/starlingx/config/src/branch/master/sysinv/sysinv/sysinv/sysinv) contains a multitude of functions and variables that may be
helpful in the development of application plugins.

### Other files

For the customization of the application the modifications above, in the FluxCD
and the plugins should be enough for the application to run as expected in the
StarlingX platform.

With that in mind, it is recommended to check if the `metadata` and the `setup.cfg`
have been created as they should. Particularly, the `setup.cfg` may need careful
attention if the modifications on the plugin file should be reflected in it.

### Packaging the application

To finish the application setup and make it ready to be deployed on your StarlingX cluster, simply run

```shell
python3 app-gen.py -i app_manifest.yaml --package-only
```

now, send the tarball to your StarlingX cluster and follow along the [demo guide](Demo.md)
