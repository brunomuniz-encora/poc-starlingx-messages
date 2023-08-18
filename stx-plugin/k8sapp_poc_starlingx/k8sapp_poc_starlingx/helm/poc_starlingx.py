from k8sapp_poc_starlingx.common import constants

from sysinv.helm import base
from sysinv.common import exception

class PocStarlingxHelm(base.BaseHelm):
    """Class to encapsulate helm operations for the poc chart"""
    
    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [constants.HELM_NS_POC_STARLINGX]
    SUPPORTED_APP_NAMESPACES = {
        constants.HELM_APP_POC_STARLINGX: SUPPORTED_NAMESPACES,
    }

    CHART = constants.HELM_CHART_POC_STARLINGX

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES


    def get_overrides(self, namespace=None):

        overrides = {}            

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

