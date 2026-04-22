from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='pass',
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='pass',
        )
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='slug',
            author=cls.author,
        )

        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')

    def test_home_available_for_anonymous(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_auth_pages_available_for_all(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.logout_url)
        self.assertIn(response.status_code, (200, 405))

        if response.status_code == 405:
            response = self.client.post(self.logout_url)
            self.assertIn(response.status_code, (200, 302))

    def test_pages_available_for_authenticated_user(self):
        client = Client()
        client.force_login(self.author)

        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_note_pages_available_only_for_author(self):
        client = Client()
        client.force_login(self.author)

        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_note_pages_return_404_for_other_user(self):
        client = Client()
        client.force_login(self.other_user)

        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_anonymous_redirects_to_login(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                expected = f'{self.login_url}?next={url}'
                self.assertEqual(response.url, expected)
