from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from billboard.management.commands.repair_nested_billboard_paths import (
    candidate_paths,
    is_nested_path,
    resolve_best_path,
)
from tests.helpers import make_billboard
from tests.helpers.media import put_storage_file


class RepairPathHelpersTests(TestCase):
    def test_is_nested_path(self):
        self.assertFalse(is_nested_path(''))
        self.assertFalse(is_nested_path('billboard/2026/10/01/a.jpg'))
        self.assertTrue(
            is_nested_path('billboard/2026/10/11/billboard/2026/10/04/photo.jpg')
        )

    def test_candidate_paths(self):
        nested = 'billboard/2026/10/11/billboard/2026/10/04/photo.jpg'
        candidates = list(candidate_paths(nested))
        self.assertEqual(candidates[0], 'billboard/2026/10/04/photo.jpg')
        self.assertIn(nested, candidates)

    def test_resolve_best_path(self):
        leaf = 'billboard/2026/10/04/photo.jpg'
        nested = 'billboard/2026/10/11/billboard/2026/10/04/photo.jpg'
        put_storage_file(leaf, b'ok')
        new_path, changed = resolve_best_path(nested)
        self.assertTrue(changed)
        self.assertEqual(new_path, leaf)
        same, changed2 = resolve_best_path(leaf)
        self.assertFalse(changed2)
        self.assertEqual(same, leaf)


class RepairCommandTests(TestCase):
    def test_dry_run_and_live(self):
        leaf = 'billboard/2026/10/04/cmd.jpg'
        nested = 'billboard/2026/10/11/billboard/2026/10/04/cmd.jpg'
        put_storage_file(leaf, b'ok')
        bb = make_billboard(name='NestedPath')
        BillboardModel = bb.__class__
        BillboardModel.objects.filter(pk=bb.pk).update(billboard_pic=nested)
        out = StringIO()
        call_command('repair_nested_billboard_paths', '--dry-run', stdout=out)
        bb.refresh_from_db()
        self.assertEqual(bb.billboard_pic.name, nested)
        call_command('repair_nested_billboard_paths', stdout=StringIO())
        bb.refresh_from_db()
        self.assertEqual(bb.billboard_pic.name, leaf)
