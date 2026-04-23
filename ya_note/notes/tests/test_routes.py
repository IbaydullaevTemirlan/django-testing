from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт данные для всех тестов класса один раз."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        """Главная и страницы регистрации/логина/логаута доступны анониму."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                if name == 'users:logout':
                    response = self.client.post(url)
                    self.assertIn(
                        response.status_code,
                        (HTTPStatus.OK, HTTPStatus.FOUND),
                    )
                else:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Страницы list/add/success доступны авторизованному пользователю."""
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        """detail/edit/delete: автору OK, не автору 404."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Аноним перенаправляется на логин при входе на защищённые страницы."""
        login_url = reverse('users:login')
        for name in (
            'notes:list',
            'notes:add',
            'notes:success',
            'notes:detail',
            'notes:edit',
            'notes:delete',
        ):
            with self.subTest(name=name):
                if name in ('notes:detail', 'notes:edit', 'notes:delete'):
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)