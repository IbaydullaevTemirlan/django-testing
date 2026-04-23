from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news(db):
    """Создаёт новость для тестов."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model, db):
    """Создаёт пользователя — автора комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model, db):
    """Создаёт пользователя, который не является автором комментария."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Возвращает клиент, авторизованный как автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Возвращает клиент, авторизованный как читатель (не автор)."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(news, author, db):
    """Создаёт комментарий к новости от имени автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def many_news(db):
    """Создаёт новости для проверки количества и сортировки на главной."""
    today = timezone.now().date()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_with_comments(news, author, db):
    """Создаёт комментарии с разным временем создания для проверки сортировки."""
    now = timezone.now()
    for index in range(10):
        created_comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        created_comment.created = now + timedelta(days=index)
        created_comment.save()


@pytest.fixture
def comment_form_data():
    """Данные формы для создания/редактирования комментария."""
    return {'text': 'Новый текст комментария'}


@pytest.fixture
def home_url():
    """URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """URL страницы отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def detail_comments_url(detail_url):
    """URL страницы новости с якорем на блок комментариев."""
    return f'{detail_url}#comments'


@pytest.fixture
def login_url():
    """URL страницы логина."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def comment_edit_url(comment):
    """URL страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    """URL страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))
