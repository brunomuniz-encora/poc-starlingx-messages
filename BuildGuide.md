
# Deploy an application as a StarlingX app

This guide describes the steps to deploy an application as
a StarlingX application.

- [FluxCD Manifest](#fluxcd-manifest)
- [Plugins](#plugins)
- [Application structure](#application-structure)

## FluxCD Manifest

The FluxCD Manifest for the StarlingX environment must follow a specific
structure. The overall, generic structure of a StarlingX FluxCD Manifest
is as follow:

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

#### kustomization.yaml

Each layer must have a `kustomization.yaml` file that contains the
resources to apply.

```shell
    apiVersion: kustomize.config.k8s.io/v1beta1
    kind: Kustomization
    namespace: <kubernetes-namespace>
    resources: # the chart directories that need to be applied
      - base
      - APP-NAME
```

### The base chart directory contains the following:

#### base/helmrepository.yaml

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

```shell
    resources:
      - helmrepository.yaml
```

#### base/namespace.yaml

```shell
    apiVersion: v1
    kind: Namespace
    metadata:
      name: <kubernetes-namespace>
```

### The APP-NAME chart directory contains the following:

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

```shell
    # the static overrides, basically all the values from the
    # values.yaml of the application
```

#### APP-NAME/APP-NAME-system-overrides.yaml

```shell
    #The APP-NAME-system-overrides.yaml is empty and will contain any 
    # system overrides or user overrides ( generated by helm plugins or
    # system helm-override-update)
```

## Plugins

The plugins for the StarlingX applications will vary for each
application, but a few files must exist for the StarlingX system to
deploy an application as an system application. For a complete overview
of different plugins used in the various applications available now for
the StarlingX you may check the various applications available in the
[StarlingX applications repository](https://opendev.org/starlingx?sort=recentupdate&language=&q=app). Some of the applications are:

- [Certificate Manager Application](https://opendev.org/starlingx/cert-manager-armada-app/src/branch/master/python3-k8sapp-cert-manager/k8sapp_cert_manager/k8sapp_cert_manager)
- [Portieris Application](https://opendev.org/starlingx/portieris-armada-app/src/branch/master/python3-k8sapp-portieris/k8sapp_portieris/k8sapp_portieris)
- [Dell Storage Application](https://opendev.org/starlingx/app-dell-storage/src/branch/master/python3-k8sapp-dell-storage/k8sapp_dell_storage/k8sapp_dell_storage)
- [Vault Application](https://opendev.org/starlingx/vault-armada-app/src/branch/master/python3-k8sapp-vault/k8sapp_vault/k8sapp_vault)

An overall structure for the plugins folder is as follow:

```shell
    python3-k8sapp-APP-NAME/
    ├── k8sapp_APP_NAME
    │   ├── common
    │   │   ├──__init__.py 
    │   │   └──
    │   ├── helm
    │   │   ├──__init__.py 
    │   │   └──
    │   ├── kustomize
    │   │   ├──__init__.py 
    │   │   └──
    │   ├── lifecycle
    │   │   ├──__init__.py 
    │   │   └──
    │   └── tests
    │       ├──__init__.py 
    │       └──
    ├── __init__.py
    ├── setup.cfg
    ├── setup.py
    └── 
```

## Application structure