import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_cannot_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    login_url = reverse('users:login')

    response = client.post(url, data={'text': 'Hello'})
    assert response.status_code == 302
    assert response.url == f'{login_url}?next={url}'
    assert Comment.objects.count() == 0


def test_authorized_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': 'Hello'})

    assert response.status_code == 302
    assert response.url == f'{url}#comments'

    comment = Comment.objects.get()
    assert comment.text == 'Hello'
    assert comment.author == author
    assert comment.news == news


def test_bad_words_comment_not_published(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_text = f'Text {BAD_WORDS[0]}'
    response = author_client.post(url, data={'text': bad_text})

    assert response.status_code == 200
    assert Comment.objects.count() == 0
    assert WARNING in response.context['form'].errors['text']


def test_author_can_edit_own_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data={'text': 'New text'})

    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == 'New text'


def test_author_can_delete_own_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)

    assert response.status_code == 302
    assert Comment.objects.filter(id=comment.id).exists() is False


def test_user_cannot_edit_foreign_comment(reader_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data={'text': 'Hack'})
    assert response.status_code == 404


def test_user_cannot_delete_foreign_comment(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == 404
    assert Comment.objects.filter(id=comment.id).exists() is True
