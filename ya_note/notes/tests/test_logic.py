from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
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
        cls.add_url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')

        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_anonymous_cannot_create_note(self):
        response = self.client.post(
            self.add_url,
            data={'title': 'T', 'text': 'X', 'slug': 's1'},
        )
        self.assertEqual(response.status_code, 302)
        expected = f'{self.login_url}?next={self.add_url}'
        self.assertEqual(response.url, expected)

    def test_authenticated_can_create_note(self):
        client = Client()
        client.force_login(self.author)

        Note.objects.all().delete()
        response = client.post(
            self.add_url,
            data={'title': 'T', 'text': 'X', 'slug': 's1'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.author, self.author)

    def test_cannot_create_two_notes_with_same_slug(self):
        client = Client()
        client.force_login(self.author)

        response = client.post(
            self.add_url,
            data={'title': 'T2', 'text': 'X2', 'slug': self.note.slug},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(WARNING, form.errors['slug'][0])

    def test_slug_is_created_automatically_if_empty(self):
        client = Client()
        client.force_login(self.author)

        title = 'Привет мир'
        Note.objects.all().delete()

        response = client.post(
            self.add_url,
            data={'title': title, 'text': 'Text', 'slug': ''},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.success_url)

        note = Note.objects.get()
        expected_slug = slugify(title)[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_edit_and_delete_own_note(self):
        client = Client()
        client.force_login(self.author)

        response = client.post(
            self.edit_url,
            data={'title': 'New', 'text': 'New text', 'slug': self.note.slug},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.success_url)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'New')

        response = client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.success_url)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cannot_edit_or_delete_foreign_note(self):
        client = Client()
        client.force_login(self.other_user)

        response = client.get(self.edit_url)
        self.assertEqual(response.status_code, 404)

        response = client.get(self.delete_url)
        self.assertEqual(response.status_code, 404)

        response = client.post(
            self.edit_url,
            data={
                'title': 'Hack',
                'text': 'Hack',
                'slug': self.note.slug,
            },
        )
        self.assertEqual(response.status_code, 404)

        response = client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
