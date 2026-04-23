from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты создания заметок и правил для slug."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'test-slug',
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_slug_is_created_if_not_set(self):
        """Если slug не заполнен, он создаётся из заголовка."""
        form_data = self.form_data.copy()
        form_data['title'] = 'Заметка без slug'
        form_data.pop('slug')

        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.success_url)

        note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_user_cant_create_note_with_existing_slug(self):
        """Нельзя создать заметку с неуникальным slug."""
        existing_note = Note.objects.create(
            title='Старая',
            text='Текст',
            slug='existing-slug',
            author=self.user,
        )
        form_data = self.form_data.copy()
        form_data['slug'] = existing_note.slug

        response = self.auth_client.post(self.add_url, data=form_data)

        form = response.context['form']
        self.assertFormError(form, 'slug', existing_note.slug + WARNING)

        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(TestCase):
    """Тесты редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.success_url = reverse('notes:success')

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        old_title = self.note.title
        old_text = self.note.text
        old_slug = self.note.slug

        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, old_title)
        self.assertEqual(note_from_db.text, old_text)
        self.assertEqual(note_from_db.slug, old_slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
