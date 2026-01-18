import json
from django.shortcuts import render


def residual_value(request):
    """
    Renders the residual value page with date options for the dropdown.
    """
    date_data = {
        "date_label": [
            "2026-01-14",
            "2026-01-13",
            "2026-01-12",
        ],
        "date_value": [
            20260114,
            20260113,
            20260112,
        ],
    }

    context = {
        "date_data_json": json.dumps(date_data),
    }

    return render(request, "residual_value.html", context)