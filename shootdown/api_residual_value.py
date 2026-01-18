import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .utils.cbbc_processor import CBBCBuilder

@require_GET
def get_residual_value(request):
    """
    Get CBBC residual value data for a specific date
    GET /api/residual-value/?date=20250117
    """
    date_str = request.GET['date']  

    if not date_str:
        return JsonResponse(
            {"error": "Missing required parameter 'date' (format: YYYYMMDD)"},
            status=400
        )

    try:
        builder = (
            CBBCBuilder(date_str)
            .load_data()
            .build_positions()
        )

        data = builder.get_cbbc_data()

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse(
            {"error": "Failed to process residual value data"},
            status=500
        )
    