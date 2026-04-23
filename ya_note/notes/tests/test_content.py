from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):
    """Тесты контента страницы со списком заметок."""

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_note_1 = Note.objects.create(
            title='B',
            text='Текст',
            slug='author-note-1',
            author=cls.author,
        )
        cls.author_note_2 = Note.objects.create(
            title='A',
            text='Текст',
            slug='author-note-2',
            author=cls.author,
        )
        cls.reader_note = Note.objects.create(
            title='Чужая',
            text='Текст',
            slug='reader-note',
            author=cls.reader,
        )

    def test_notes_list_contains_only_author_notes(self):
        """В список попадают только заметки текущего пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 2)
        self.assertIn(self.author_note_1, object_list)
        self.assertIn(self.author_note_2, object_list)
        self.assertNotIn(self.reader_note, object_list)

    def test_notes_order(self):
        """Заметки в списке отсортированы по id (от старых к новым)."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        ids = [note.id for note in object_list]
        self.assertEqual(ids, sorted(ids))


class TestNoteFormPages(TestCase):
    """Тесты контента страниц с формой создания и редактирования."""

    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_form_on_add_page(self):
        """Авторизованному передаётся форма на странице добавления."""
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_on_edit_page(self):
        """Авторизованному передаётся форма на странице редактирования."""
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
