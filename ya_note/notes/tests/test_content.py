from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Проверки контента и контекста страниц (без анализа HTML)."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт пользователей и заметки для проверки контекста."""
        cls.author = User.objects.create_user(
            username='author',
            password='pass',
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='pass',
        )
        cls.author_note = Note.objects.create(
            title='Author title',
            text='Author text',
            slug='author-slug',
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title='Other title',
            text='Other text',
            slug='other-slug',
            author=cls.other_user,
        )

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.author_note.slug,))

    def test_note_in_object_list_in_context(self):
        """На странице списка заметок заметка автора есть в object_list."""
        client = Client()
        client.force_login(self.author)

        response = client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.author_note, object_list)

    def test_other_users_notes_not_in_list(self):
        """В список заметок пользователя не попадают заметки другого пользователя."""
        client = Client()
        client.force_login(self.author)

        response = client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.author_note, object_list)
        self.assertNotIn(self.other_note, object_list)

    def test_forms_on_add_and_edit_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        client = Client()
        client.force_login(self.author)

        response = client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        response = client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
