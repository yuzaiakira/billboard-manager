"""
Safely repair nested billboard image paths in the database.

Does not delete files or change schema. Prefer the shortest existing path
on storage; leave the DB value unchanged when no candidate exists.

Usage:
  python manage.py repair_nested_billboard_paths --dry-run
  python manage.py repair_nested_billboard_paths
"""

import os
import re

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from billboard.models import BillboardImageModel, BillboardModel


def is_nested_path(path: str) -> bool:
    if not path:
        return False
    return path.count('billboard/') > 1


def candidate_paths(path: str):
    """Yield preferred repair candidates, leaf/short first."""
    if not path:
        return

    basename = os.path.basename(path)
    segments = re.findall(r'billboard/\d{4}/\d{2}/\d{2}', path)
    seen = set()

    if segments:
        leaf = '{}/{}'.format(segments[-1], basename)
        if leaf not in seen:
            seen.add(leaf)
            yield leaf

        for segment in reversed(segments[:-1]):
            candidate = '{}/{}'.format(segment, basename)
            if candidate not in seen:
                seen.add(candidate)
                yield candidate

    collapsed = re.sub(
        r'(?:billboard/\d{4}/\d{2}/\d{2}/)+(?=billboard/\d{4}/\d{2}/\d{2}/)',
        '',
        path,
    )
    if collapsed not in seen:
        seen.add(collapsed)
        yield collapsed

    if path not in seen:
        yield path


def resolve_best_path(path: str):
    """Return the best existing storage path for a nested DB value."""
    if not is_nested_path(path):
        return path, False

    for candidate in candidate_paths(path):
        try:
            if default_storage.exists(candidate):
                return candidate, candidate != path
        except Exception:
            continue

    try:
        if default_storage.exists(path):
            return path, False
    except Exception:
        pass

    return path, False


class Command(BaseCommand):
    help = 'Repair nested billboard image paths in DB without deleting files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show changes without writing to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated = 0
        scanned = 0

        updates = [
            (BillboardModel, 'billboard_pic'),
            (BillboardImageModel, 'image'),
        ]

        for model, field_name in updates:
            qs = model.objects.exclude(**{field_name: ''}).exclude(
                **{'{}__isnull'.format(field_name): True}
            ).only('pk', field_name)

            for obj in qs.iterator():
                field_file = getattr(obj, field_name)
                path = field_file.name if field_file else ''
                if not path:
                    continue
                scanned += 1
                if not is_nested_path(path):
                    continue

                new_path, changed = resolve_best_path(path)
                if not changed:
                    self.stdout.write(
                        'skip {}#{} (no shorter existing path): {}'.format(
                            model.__name__, obj.pk, path
                        )
                    )
                    continue

                self.stdout.write(
                    '{} {}#{}: {} -> {}'.format(
                        'would update' if dry_run else 'update',
                        model.__name__,
                        obj.pk,
                        path,
                        new_path,
                    )
                )
                if not dry_run:
                    # Direct UPDATE avoids ImageField save/upload_to side effects.
                    model.objects.filter(pk=obj.pk).update(**{field_name: new_path})
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            'Scanned {}, {} {}.'.format(
                scanned,
                updated,
                'would be updated' if dry_run else 'updated',
            )
        ))
