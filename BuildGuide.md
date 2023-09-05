# Deploy an application as a StarlingX app

This guide describes the steps to deploy an application as a **StarlingX App**.

- [Prerequisites](#prerequisites)
- [FluxCD Manifest](#fluxcd-manifest)
- [Plugins](#plugins)
- [Application structure](#application-structure)
- [Packaging the application](#packaging-the-application)

## Prerequisites

As the StarlingX Platform manages a distributed Kubernetes cluster, for an
application to be deployed as a StarlingX App it needs to be designed so it can
run on [Kubernetes](https://kubernetes.io/).

Additionally, it needs to provide a [Helm Chart](https://helm.sh/) which will be managed
via [Flux](https://fluxcd.io/).

## FluxCD Manifest

The FluxCD Manifest for the StarlingX App must follow a specific structure.
The overall, generic structure of a StarlingX App's FluxCD Manifest is as 
follows:

> _NOTE_: `APP-NAME` is a placeholder and should change according to your app's 
name and/or dependencies that your app may need.

```shell
fluxcd-manifests/
├── base
│   ├── helmrepository.yaml
│   ├── kustomization.yaml
│   └── namespace.yaml
├── kustomization.yaml
└── APP-NAME
    ├── helmrelease.yaml
    ├── kustomization.yaml
    ├── APP-NAME-static-overrides.yaml
    └── APP-NAME-system-overrides.yaml
```

An application may make use of multiple folders of APP-NAME containing
different `helmrelease.yaml` for each one. An example of this can be
seen in the [Dell Storage app](https://opendev.org/starlingx/app-dell-storage/src/branch/master/stx-dell-storage-helm/stx-dell-storage-helm/fluxcd-manifests)
for StarlingX.

### The `flux-manifests` (root) directory

#### `kustomization.yaml`

A `kustomization.yaml` file is required in the `flux-manifests` (root) directory
, tying all the different Helm releases together. For example:

```shell
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: <kubernetes-namespace>
resources: # the chart directories that need to be applied
  - base
  - APP-NAME
  - ...
```

>_NOTE_: each "APP_NAME" directory and the `base` directory require its own
`kustomization.yaml` file, which will be explained in the sections below.

### The base chart directory

The base chart directory contains the following:

#### base/helmrepository.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
# HelmRepository YAML for StarlingX helm repository.
apiVersion: source.toolkit.fluxcd.io/v1beta1
kind: HelmRepository
metadata:
  name: stx-platform
spec:
  url: http://<cluster_host_ip>:8080/helm_charts/stx-platform
  # The cluster host ip is 192.168.206.1 if it wasn't changed during
  # bootstrap
  interval: 60m  # interval to check the repository for updates
```

#### base/kustomization.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
resources:
  - helmrepository.yaml
```

#### base/namespace.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
apiVersion: v1
kind: Namespace
metadata:
  name: <kubernetes-namespace>
```

### The APP-NAME chart directory

The APP-NAME chart directory contains the following:

#### APP-NAME/helmrelease.yaml

```shell
apiVersion: "helm.toolkit.fluxcd.io/v2beta1"
kind: HelmRelease
metadata:
  name: APP-NAME
  labels:
    chart_group: APP-NAME
spec:
  releaseName: APP-NAME
  chart: 
  # A HelmChart CR of a specific chart is auto created in the
  # cluster with this definition
    spec:
      chart: CHART-NAME
      version: VERSION
      sourceRef:
        kind: HelmRepository
        name: stx-platform
  interval: 5m  # Interval to reconcile Helm release
  timeout: 30m
  test:
    enable: false
  install:
    disableHooks: false
  upgrade:
    disableHooks: false
  valuesFrom:
  # We store the static overrides and the system 
  # overrides in k8s Secrets, the 2 yaml files are present in 
  # the same directory with this file
    - kind: Secret
    name: APP-NAME-static-overrides
    valuesKey: APP-NAME-static-overrides.yaml
    - kind: Secret
    name: APP-NAME-system-overrides
    valuesKey: APP-NAME-system-overrides.yaml
```

#### APP-NAME/kustomization.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
namespace: <NAMESPACE>
resources:
- helmrelease.yaml
secretGenerator:  
# this will create the Secrets (that hold the 
# overrides) as part of application install
  - name: APP-NAME-static-overrides
    files:
      - APP-NAME-static-overrides.yaml
  - name: APP-NAME-system-overrides
    files:
      - APP-NAME-system-overrides.yaml
generatorOptions:
  disableNameSuffixHash: true
```

#### APP-NAME/APP-NAME-static-overrides.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
# The static overrides, basically all the values from the
# values.yaml of the application
```

#### APP-NAME/APP-NAME-system-overrides.yaml

[//]: # (TODO: This needs further explanation or a paragraph here.)

```shell
# The APP-NAME-system-overrides.yaml is empty and will contain any 
# system overrides or user overrides ( generated by helm plugins or
# system helm-override-update)
```

## Plugins

The plugins for the StarlingX Apps will vary from one application to another,
however, a handful of files must exist for the StarlingX Platform to deploy the
StarlingX App. For a complete overview of different plugins used in the
various applications available now for StarlingX see 
[StarlingX applications repository search](https://opendev.org/starlingx?sort=recentupdate&language=&q=app)
.

Here are some examples:

- [Certificate Manager Application](https://opendev.org/starlingx/cert-manager-armada-app/src/branch/master/python3-k8sapp-cert-manager/k8sapp_cert_manager/k8sapp_cert_manager)
- [Portieris Application](https://opendev.org/starlingx/portieris-armada-app/src/branch/master/python3-k8sapp-portieris/k8sapp_portieris/k8sapp_portieris)
- [Dell Storage Application](https://opendev.org/starlingx/app-dell-storage/src/branch/master/python3-k8sapp-dell-storage/k8sapp_dell_storage/k8sapp_dell_storage)
- [Vault Application](https://opendev.org/starlingx/vault-armada-app/src/branch/master/python3-k8sapp-vault/k8sapp_vault/k8sapp_vault)

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

* `constants.py`: This file is used to hold the constants that will be used on
  the plugin(s).

* `helm/APP_NAME.py`: File responsible for overriding methods that will be used
  to create the Helm overrides for the StarlingX App. Usually for every APP_NAME
  folder in the FluxCD Manifest, an APP_NAME.py plugin is used to create its 
  overrides.

* `kustomize_APP_NAME.py`: This plugin is used to make changes to the top-level
  kustomization resource list based on the platform mode.

* `lifecycle_APP_NAME.py`: Responsible for performing lifecycle actions on the
  application using the lifecycle hooks of the StarlingX Platform.

* `test.py`: File or files that holds unit tests for the application and 
  plugins.

It is important to notice that most of the files above, although nice to have,
are not mandatory. Files like the `kustomize_*` and `lifecycle_*` plugins will only
exist if the application itself requires that these types of actions are 
necessary.

The only mandatory file is the `helm/APP_NAME.py` plugin, which is responsible
for creating the overrides for the application on the StarlingX Platform. An
example can be seen below:

```shell
from k8sapp_APP_NAME.common import constants
from sysinv.common import exception # import from the StarlingX Platform
from sysinv.helm import base # import from the StarlingX Platform

class AppNameHelm(base.FluxCDBaseHel):
    """Class to encapsulate helm operations for the psp role-binding chart"""

    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [constants.HELM_NS_APP_NAME]
    SUPPORTED_APP_NAMESPACES = {
        constants.HELM_APP_APP_NAME:
            base.BaseHelm.SUPPORTED_NAMESPACES + [constants.HELM_NS_APP_NAME],
    }

    CHART = constants.HELM_CHART_APP_NAME
    HELM_RELEASE = constants.FLUXCD_HELMRELEASE_APP_NAME 

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES


    def get_overrides(self, namespace=None):
        overrides = {
            constants.HELM_NS_APP_NAME: {
                # This function returns the full overrides used in the
                # application. If your application don't have static overrides
                # this functions should still exist with an empty
                # implementation.
            }
        }

    if namespace in self.SUPPORTED_NAMESPACES:
        return overrides[namespace]
    elif namespace:
        raise exception.InvalidHelmNamespace(chart=self.CHART,
                                             namespace=namespace)
    else:
        return overrides
```

The above file is an example of the most basic implementation of the plugin.
This example returns an empty override. Usually, in this case, the full override
will be given by the user using `system helm-override-update` within the
StarlingX Platform upon deployment of the StarlingX App.

An optional file, which we suggested that you make use of, is the
`common/constants.py` file, which will hold the constants used on the
plugins. A generic example of this file could be:

```shell
# Application Name
HELM_APP_APP_NAME = 'app-name'

#Namespace
HELM_NS_APP_NAME = 'namespace'

# Helm: Supported charts:
HELM_CHART_APP_NAME = 'helm-chart-name'

# FluxCD
FLUXCD_HELMRELEASE_APP_NAME = 'fluxcd-chart-name'
```

The `sysinv` folder in the [StarlingX config repository](https://opendev.org/starlingx/config/src/branch/master/sysinv/sysinv/sysinv/sysinv)
contains a multitude of functions and variables that may be helpful in the
development of application plugins.

Finally, the `test.py` file, although not mandatory, is considered a good coding
practice to test the StarlingX App and its plugins. If your app will be
integrated to the StarlingX Platform and managed by the community, tests are
mandatory.

### Other files

[//]: # (This section needs help from the Community)

Below is an example implementation of the `setup.py` file:

```shell
import setuptools

setuptools.setup(
    setup_requires=['pbr>=2.0.0'],
    pbr=True)
```

The `setup.cfg` file implementation, although longer, is easy, as most of the 
implementation follows a recipe:

```shell
[metadata]
name = k8sapp-APP-NAME
summary = StarlingX sysinv extensions for app-name
author = <Author or teams name>
author-email = <Author or team email>
url = <Url for the application>
classifier =
    Operating System :: OS Independent
    License :: OSI Approved :: MIT License
    # The language will be exclusive of each application
    Programming Language :: Python :: 3

[options]
install_requires =
    # Requirements for the application

[files]
packages =
    k8sapp_APP_NAME

[global]
setup-hooks =
    pbr.hooks.setup_hook

[entry_points]
systemconfig.helm_applications =
    dell-storage = systemconfig.helm_plugins.APP_NAME

systemconfig.helm_plugins.APP_NAME =
    001_APP-NAME = k8sapp_APP_NAME.helm.APP_NAME:AppNameHelm
    # If the application requires more than one plugin in the helm folder
    # to generate the overrides, the other files must also be listed here.

systemconfig.fluxcd.kustomize_ops =
    APP_NAME = k8sapp_APP_NAME.kustomize.kustomize_APP_NAME:AppNameFluxCDKustomizeOperator

systemconfig.app_lifecycle =
    APP-NAME = k8sapp_APP_NAME.lifecycle.lifecycle_APP_NAME:AppNameAppLifecycleOperator

[bdist_wheel]
universal = 1
```

## Application structure

The final structure for the application is composed of the plugin(s), the FluxCD
manifest and a `metadata.yml` file inside the folder containing the manifest:

```shell
    APP-NAME/
    ├── helm-charts/
    ├── stx-APP-NAME-helm
    │   ├── fluxcd-manifests/
    │   └── metadata.yaml
    └── python3-k8sapp-APP-NAME/
```

>_NOTE_: This specific structure is a simplified format that can be built
outside the StarlingX build environment and deployed independently on any
StarlingX instance. For a more robust StarlingX build environment and expected
community structure refer to the [official wiki page](https://wiki.openstack.org/wiki/StarlingX/Containers/HowToAddNewFluxCDAppInSTX)
. You will find instructions on how to create and add an application to the
StarlingX repository/community.

The `helm-charts` folder contains the helm charts necessary to deploy your
StarlingX App on Kubernetes.

The `metadata.yaml` file is necessary to enable some features of the StarlingX
Platform. This is a template for this file:

```shell
app_name: <name>
app_version: <version>
upgrades:
  auto_update: <true/false/yes/no>
  update_failure_no_rollback: <true/false/yes/no>
  from_versions:
  - <version.1>
  - <version.2>
supported_k8s_version:
  minimum: <version>
  maximum: <version>
supported_releases:
  <release>:
  - <patch.1>
  - <patch.2>
  ...
repo: <helm repo> - optional: defaults to HELM_REPO_FOR_APPS
disabled_charts: - optional: charts default to enabled
- <chart name>
- <chart name>
...
maintain_user_overrides: <true|false>
  - optional: defaults to false. Over an app update any user overrides are
    preserved for the new version of the application
...
behavior: - optional: describes the app behavior
    platform_managed_app: <true/false/yes/no> - optional: when absent behaves as false
    desired_state: <uploaded/applied> - optional: state the app should reach
    evaluate_reapply: - optional: describe the reapply evaluation behaviour
        after: - optional: list of apps that should be evaluated before the current one
          - <app_name.1>
          - <app_name.2>
        triggers: - optional: list of what triggers the reapply evaluation
          - type: <key in APP_EVALUATE_REAPPLY_TRIGGER_TO_METADATA_MAP>
            filters: - optional: list of field:value, that aid filtering
                of the trigger events. All pairs in this list must be
                present in trigger dictionary that is passed in
                the calls (eg. trigger[field_name1]==value_name1 and
                trigger[field_name2]==value_name2).
                Function evaluate_apps_reapply takes a dictionary called
                'trigger' as parameter. Depending on trigger type this
                may contain custom information used by apps, for example
                a field 'personality' corresponding to node personality.
                It is the duty of the app developer to enhance existing
                triggers with the required information.
                Hard to obtain information should be passed in the trigger.
                To use existing information it is as simple as defining
                the metadata.
              - <field_name.1>: <value_name.1>
              - <field_name.2>: <value_name.2>
            filter_field: <field_name> - optional: field name in trigger
                          dictionary. If specified the filters are applied
                          to trigger[filter_field] sub-dictionary instead
                          of the root trigger dictionary.
apply_progress_adjust: - optional: Positive integer value by which to adjust the
                                   percentage calculations for the progress of
                                   a monitoring task.
                                   Default value is zero (no adjustment)
```

For a better understanding of each of the attributes in this yaml file refer to
[this link](https://wiki.openstack.org/wiki/StarlingX/Containers/StarlingXAppsInternals#metadata.yaml)
in order to determine the necessary attributes for your application.

## Packaging the application

As said before, the StarlingX community offers an environment to build
applications and the StarlingX Platform `.iso` file itself. In order to deploy
this environment you can follow the instructions on [this link](https://wiki.openstack.org/wiki/StarlingX/DebianBuildEnvironment).
Alternatively you can use the [tis-repo repository](https://opendev.org/starlingx/tis-repo)
to create the StarlingX build environment using Vagrant/VirtualBox.

However, you don't need the whole StarlingX Platform source code to package your
application into a StarlingX App package.

Below is an example of how this can be achieved using the structure provided in
this repository:

```shell
export APP_NAME="app_name"
```

```shell
# Assuming you Helm chart source code is in the helm-chart directory.
# Package the helm charts:
helm package helm-chart/

# Assuming the StarlingX Plugin is in the directory stx-plugin/k8sapp_${APP_NAME}.
# Package the plugin(s) in the Wheel format:
cd stx-plugin; \
python3 setup.py bdist_wheel -d k8sapp_${APP_NAME}
## Clean up files and folders
rm -r build/ \
k8sapp_${APP_NAME}.egg-info/ \
AUTHORS ChangeLog


# Assuming that the template for your StarlingX App package is in ./stx-packaging
# Assuming your Helm chart's name is $APP_NAME 
# Package the StarlingX App:
## Create folders inside ./stx-packaging/ for the chart and plugin packages
mkdir -p stx-packaging/charts
mkdir -p stx-packaging/plugins
## Move the helm charts package to the stx-packaging/charts folder
mv ${APP_NAME}*.tgz stx-packaging/charts/
## Move the plugin (wheel package) to the stx-packaging/plugins folder
mv stx-plugin/k8sapp_${APP_NAME}/k8sapp_${APP_NAME}*.whl stx-packaging/plugins/
## Create a sha256 checksum
cd stx-packaging; find . -type f ! -name '*.sha256' -print0 | xargs -0 sha256sum > ../${APP_NAME}-stx-pkg.tar.gz.sha256
## Compress everything into the StarlingX App package
cd stx-packaging; tar -czvf ../${APP_NAME}-stx-pkg.tar.gz *
## Clean up files and folders
rm -r stx-packaging/charts/
rm -r stx-packaging/plugins/
```