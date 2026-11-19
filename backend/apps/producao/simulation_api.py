from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CompanyMember
from .services.simulation import reconcile_company


class SimulationMutationMixin:
    """Reconcile before changing availability or planning another order."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            reconcile_company(request.user.empresa_id)

    def finalize_response(self, request, response, *args, **kwargs):
        # Capture a newly opened pause immediately, even if no tab polls again
        # before it is closed. The before/after clocks bracket the mutation.
        if 200 <= response.status_code < 300 and request.method not in (
            "GET",
            "HEAD",
            "OPTIONS",
        ):
            reconcile_company(request.user.empresa_id)
        return super().finalize_response(request, response, *args, **kwargs)


class SimulationSyncView(APIView):
    permission_classes = [CompanyMember]

    def post(self, request):
        enabled = reconcile_company(request.user.empresa_id)
        response = Response({"simulacao_sob_demanda": enabled})
        response["Cache-Control"] = "no-store"
        return response
