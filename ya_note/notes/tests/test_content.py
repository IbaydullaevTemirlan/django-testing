from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):
    """Тесты контента страницы со списком заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.list_url = reverse('notes:list')

        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок автора',
            text='Текст',
            slug='author-note',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """Заметка видна только автору."""
        cases = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, expected in cases:
            with self.subTest(expected=expected):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected)


class TestNoteFormPages(TestCase):
    """Тесты контента страниц с формой создания и редактирования."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_pages_contains_form(self):
        """На страницах добавления и редактирования есть форма."""
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
