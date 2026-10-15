from django.test import TestCase

from tests.helpers import make_state


class SEOBaseModelTests(TestCase):
    def test_empty_slug_becomes_id(self):
        state = make_state(name='Fars', slug='')
        state.refresh_from_db()
        self.assertEqual(state.slug, str(state.id))

    def test_slug_is_slugified_with_unicode(self):
        state = make_state(name='Esfahan', slug='اصفهان شهر')
        state.refresh_from_db()
        self.assertTrue(state.slug)
        self.assertNotIn(' ', state.slug)

    def test_str(self):
        state = make_state(name='Yazd')
        self.assertEqual(str(state), 'Yazd')
