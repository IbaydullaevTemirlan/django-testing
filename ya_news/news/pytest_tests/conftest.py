import pytest
from django.contrib.auth import get_user_model

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author', password='pass')


@pytest.fixture
def reader(db):
    return User.objects.create_user(username='reader', password='pass')


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(client, reader):
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Title', text='Text')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news, author=author, text='Old text')
