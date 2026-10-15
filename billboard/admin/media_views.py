from django.http import JsonResponse
from django.views.decorators.http import require_GET

from billboard.media_library import list_media_for_user


@require_GET
def media_library_json(request):
    """JSON endpoint for the admin media library picker."""
    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.GET.get('page_size', 24))
    except (TypeError, ValueError):
        page_size = 24

    payload = list_media_for_user(
        request.user,
        query=request.GET.get('q', ''),
        page=page,
        page_size=page_size,
    )
    return JsonResponse(payload)
