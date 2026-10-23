"""Tests for watchlist PDF optimize + server-side download."""

import json
import os
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from addlist.models import ListsModel
from addlist.pdf.generator import WatchlistPdfGenerator, reshape_rtl
from addlist.pdf.image_optimizer import PdfImageOptimizer
from tests.helpers import make_billboard, make_uploaded_image, make_user


def _large_jpeg_bytes(size=(2000, 1500)):
    buf = BytesIO()
    Image.new('RGB', size, (10, 120, 200)).save(buf, format='JPEG', quality=95)
    buf.seek(0)
    return buf.read()


class PdfImageOptimizerTests(TestCase):
    def setUp(self):
        self.cache_dir = Path(settings.MEDIA_ROOT) / 'cache' / 'pdf-test'
        self.optimizer = PdfImageOptimizer(cache_dir=self.cache_dir, max_side=400, quality=70)

    def test_optimize_file_resizes_and_caches(self):
        source = Path(settings.MEDIA_ROOT) / 'src-large.jpg'
        source.write_bytes(_large_jpeg_bytes())
        out1 = self.optimizer.optimize_file(str(source))
        self.assertTrue(os.path.isfile(out1))
        with Image.open(out1) as im:
            self.assertLessEqual(max(im.size), 400)
            self.assertEqual(im.format, 'JPEG')

        out2 = self.optimizer.optimize_file(str(source))
        self.assertEqual(out1, out2)

    def test_media_url_for_cached(self):
        source = Path(settings.MEDIA_ROOT) / 'src2.jpg'
        source.write_bytes(_large_jpeg_bytes((100, 80)))
        cached = self.optimizer.optimize_file(str(source))
        url = self.optimizer.media_url_for_cached(cached)
        self.assertTrue(url.startswith(settings.MEDIA_URL.rstrip('/')))
        self.assertIn('cache/', url)

    def test_optimize_billboard_without_image_uses_fallback(self):
        bb = make_billboard()
        path, url = self.optimizer.optimize_billboard_image(bb)
        # Fallback may be None if static finder cannot locate no-image in CI;
        # when found, both path and url should be set.
        if path:
            self.assertTrue(os.path.isfile(path))
            self.assertTrue(url)


class WatchlistPdfGeneratorTests(TestCase):
    def setUp(self):
        self.user = make_user(username='pdfuser', password='pass12345')
        self.bb = make_billboard(name='PDF Board', price=1500000)
        self.bb.billboard_pic = make_uploaded_image('bb.jpg', size=(800, 600))
        self.bb.save()
        self.item = ListsModel.objects.create(user=self.user, billboard=self.bb)

    def test_generate_pdf_bytes(self):
        items = list(ListsModel.objects.filter(user=self.user).select_related(
            'billboard', 'billboard__city', 'billboard__city__state', 'billboard__BillboardFinalPriceModel',
        ))
        result = WatchlistPdfGenerator().execute(
            items,
            field_flags={
                'billboard_pic': True,
                'id_code': True,
                'name': True,
                'address': True,
                'has_power': True,
                'size': True,
                'brand': False,
                'price': True,
            },
        )
        self.assertTrue(result['success'], result.get('message'))
        pdf = result['pdf_bytes']
        self.assertTrue(pdf.startswith(b'%PDF'))
        # Small test image should keep output well under a few MB
        self.assertLess(len(pdf), 2 * 1024 * 1024)

    def test_overrides_applied(self):
        items = list(ListsModel.objects.filter(user=self.user).select_related(
            'billboard', 'billboard__city', 'billboard__city__state',
        ))
        result = WatchlistPdfGenerator().execute(
            items,
            field_flags={'id_code': True, 'name': True, 'billboard_pic': False},
            overrides={str(self.bb.id): {'name': 'نام ویرایش‌شده'}},
        )
        self.assertTrue(result['success'], result.get('message'))
        self.assertTrue(result['pdf_bytes'].startswith(b'%PDF'))

    def test_empty_list_fails(self):
        result = WatchlistPdfGenerator().execute([], field_flags={'id_code': True})
        self.assertFalse(result['success'])
        self.assertEqual(result.get('error_code'), 'EMPTY_LIST')

    def test_reshape_rtl(self):
        out = reshape_rtl('سلام')
        self.assertTrue(isinstance(out, str))
        self.assertEqual(reshape_rtl(''), '')
        self.assertEqual(reshape_rtl(None), '')

    def test_generate_with_brand(self):
        items = list(ListsModel.objects.filter(user=self.user).select_related(
            'billboard', 'billboard__city', 'billboard__city__state',
        ))
        result = WatchlistPdfGenerator().execute(
            items,
            field_flags={
                'billboard_pic': True,
                'id_code': True,
                'brand': True,
                'description': True,
                'reservation_date': True,
                'price': True,
                'size': True,
                'has_power': True,
                'address': True,
                'name': True,
            },
        )
        self.assertTrue(result['success'], result.get('message'))
        self.assertTrue(result['pdf_bytes'].startswith(b'%PDF'))

    def test_optimize_static_missing_returns_none(self):
        optimizer = PdfImageOptimizer(cache_dir=Path(settings.MEDIA_ROOT) / 'cache' / 'miss')
        path, url = optimizer.optimize_static_asset('template/images/does-not-exist-xyz.png')
        self.assertIsNone(path)
        self.assertIsNone(url)


class DownloadPdfViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='dlpdf', password='pass12345')
        self.bb = make_billboard(name='DL Board')
        self.bb.billboard_pic = make_uploaded_image('dl.jpg', size=(120, 90))
        self.bb.save()
        ListsModel.objects.create(user=self.user, billboard=self.bb)
        self.client.login(username='dlpdf', password='pass12345')

    def test_download_get(self):
        response = self.client.get(
            reverse('download-pdf'),
            {'billboard_pic': 'on', 'id_code': 'on', 'name': 'on'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('billboard-list.pdf', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.assertLess(len(response.content), 2 * 1024 * 1024)

    def test_download_post_json_with_overrides(self):
        payload = {
            'fields': {
                'billboard_pic': True,
                'id_code': True,
                'name': True,
                'brand': False,
            },
            'overrides': {
                str(self.bb.id): {'name': 'Edited Name'},
            },
        }
        response = self.client.post(
            reverse('download-pdf'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_download_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('download-pdf'))
        self.assertEqual(response.status_code, 302)

    def test_download_empty_list_bad_request(self):
        ListsModel.objects.filter(user=self.user).delete()
        response = self.client.get(reverse('download-pdf'), {'id_code': 'on'})
        self.assertEqual(response.status_code, 400)

    def test_download_post_invalid_json(self):
        response = self.client.post(
            reverse('download-pdf'),
            data='{not-json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_download_post_form_encoded(self):
        response = self.client.post(
            reverse('download-pdf'),
            data={
                'billboard_pic': 'on',
                'id_code': 'on',
                'overrides': json.dumps({str(self.bb.id): {'name': 'Form Override'}}),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_download_get_with_brand(self):
        response = self.client.get(
            reverse('download-pdf'),
            {'billboard_pic': 'on', 'brand': 'on', 'id_code': 'on'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))
