from k8sapp_poc_starlingx.common import constants
from sysinv.helm import kustomize_base as base


class PocStarlingxFluxCDKustomizeOperator(base.FluxCDKustomizeOperator):

    APP = constants.HELM_APP_POC_STARLINGX

    def platform_mode_kustomize_updates(self, dbapi, mode):
        """ Update the top-level kustomization resource list

        Make changes to the top-level kustomization resource list based on the
        platform mode

        :param dbapi: DB api object
        :param mode: mode to control when to update the resource list
        """
        pass
