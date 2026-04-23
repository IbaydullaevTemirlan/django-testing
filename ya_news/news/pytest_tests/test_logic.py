from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, comment_form_data):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Комментарий с запрещёнными словами не публикуется, форма возвращает ошибку."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалить свой комментарий."""
    delete_url = reverse('news:delete', args=(comment.id,))
    detail_url = reverse('news:detail', args=(comment.news.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Авторизованный пользователь не может удалить чужой комментарий."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, edited_comment_form_data):
    """Авторизованный пользователь может редактировать свой комментарий."""
    edit_url = reverse('news:edit', args=(comment.id,))
    detail_url = reverse('news:detail', args=(comment.news.id,))
    response = author_client.post(edit_url, data=edited_comment_form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == edited_comment_form_data['text']


def test_user_cant_edit_comment_of_another_user(reader_client, comment, edited_comment_form_data):
    """Авторизованный пользователь не может редактировать чужой комментарий."""
    old_text = comment.text
    edit_url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(edit_url, data=edited_comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
