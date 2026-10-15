"""Helpers for listing reusable billboard media paths."""

from typing import Dict, List, Optional

from django.core.files.storage import default_storage
from django.db.models import Q

from account.models import UserModel
from billboard.models import BillboardImageModel, BillboardModel


def _basename(path: str) -> str:
    return path.rsplit('/', 1)[-1] if path else ''


def _collect_paths_for_user(user) -> List[str]:
    """Return distinct non-empty image paths visible to the given user."""
    if user.user_group == UserModel.ADMIN_USER:
        billboard_qs = BillboardModel.objects.all()
        image_qs = BillboardImageModel.objects.all()
    else:
        billboard_qs = BillboardModel.objects.filter(reseller=user)
        image_qs = BillboardImageModel.objects.filter(
            Q(billboard__reseller=user) | Q(uploader=user)
        )

    paths = set()
    for path in billboard_qs.exclude(billboard_pic='').exclude(
        billboard_pic__isnull=True
    ).values_list('billboard_pic', flat=True):
        if path:
            paths.add(path)

    for path in image_qs.exclude(image='').exclude(image__isnull=True).values_list(
        'image', flat=True
    ):
        if path:
            paths.add(path)

    return sorted(paths, key=lambda p: p.lower(), reverse=True)


def list_media_for_user(
    user,
    query: str = '',
    page: int = 1,
    page_size: int = 24,
) -> Dict:
    """
    List reusable media items for admin picker.

    Only includes paths that still exist on storage.
    """
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 24), 100))
    query = (query or '').strip().lower()

    paths = _collect_paths_for_user(user)
    if query:
        paths = [
            p for p in paths
            if query in p.lower() or query in _basename(p).lower()
        ]

    existing: List[str] = []
    for path in paths:
        try:
            if default_storage.exists(path):
                existing.append(path)
        except Exception:
            continue

    total = len(existing)
    start = (page - 1) * page_size
    end = start + page_size
    page_paths = existing[start:end]

    results = []
    for path in page_paths:
        try:
            url = default_storage.url(path)
        except Exception:
            url = ''
        results.append({
            'path': path,
            'url': url,
            'name': _basename(path),
        })

    return {
        'results': results,
        'page': page,
        'page_size': page_size,
        'total': total,
        'has_next': end < total,
        'has_prev': page > 1,
    }


def resolve_library_path(path: Optional[str]) -> Optional[str]:
    """Validate a library path and return it if it exists on storage."""
    if not path:
        return None
    path = path.strip().lstrip('/')
    if not path or '..' in path.split('/'):
        return None
    if not default_storage.exists(path):
        return None
    return path
