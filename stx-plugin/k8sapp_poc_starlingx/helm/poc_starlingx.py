from k8sapp_poc_starlingx.common import constants

from sysinv.helm import base
from sysinv.common import exception


class PocStarlingxHelm(base.FluxCDBaseHelm):
    """Class to encapsulate helm operations for the poc chart"""

    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [constants.HELM_NS_POC_STARLINGX]
    SUPPORTED_APP_NAMESPACES = {
        constants.HELM_APP_POC_STARLINGX: SUPPORTED_NAMESPACES,
    }

    CHART = constants.HELM_CHART_POC_STARLINGX
    HELM_RELEASE = constants.FLUXCD_HELMRELEASE_POC_STARLINGX

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES

    def get_overrides(self, namespace=None):

        overrides = {
            constants.HELM_NS_POC_STARLINGX: {
                "env": [
                    {"name": "MODE", "value": "central"}
                ],
                "image": {
                    "repository": "docker.io/brunomuniz/poc-starlingx",
                    "tag": "latest",
                    "containerPort": "8000"
                },
                "kube": {
                    "port": 31234,
                    "replicas": 1,
                    "name": "poc-starlingx"
                }
            },
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

