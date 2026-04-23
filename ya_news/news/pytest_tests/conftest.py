from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
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
def news_args(news):
    """Возвращает args для reverse() страницы новости."""
    return (news.id,)


@pytest.fixture
def comment_args(comment):
    """Возвращает args для reverse() редактирования/удаления комментария."""
    return (comment.id,)


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
def news_with_comments(author, db):
    """Создаёт новость и комментарии с разным временем создания."""
    news = News.objects.create(title='Тестовая новость', text='Просто текст.')
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def comment_form_data():
    """Данные формы для создания комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def edited_comment_form_data():
    """Данные формы для редактирования комментария."""
    return {'text': 'Обновлённый комментарий'}