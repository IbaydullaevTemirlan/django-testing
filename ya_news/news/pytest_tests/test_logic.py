from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
    client,
    detail_url,
    comment_form_data,
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    detail_comments_url,
    comment_form_data,
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=comment_form_data)
    assertRedirects(response, detail_comments_url)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    """Стоп-слова: форма возвращает ошибку, комментарий не создаётся."""
    text = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(detail_url, data={'text': text})
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client,
    comment_delete_url,
    detail_comments_url,
):
    """Автор может удалить свой комментарий."""
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, detail_comments_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    reader_client,
    comment_delete_url,
):
    """Пользователь не может удалить чужой комментарий."""
    response = reader_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client,
    comment,
    comment_edit_url,
    detail_comments_url,
    comment_form_data,
):
    """Автор может редактировать свой комментарий."""
    response = author_client.post(comment_edit_url, data=comment_form_data)
    assertRedirects(response, detail_comments_url)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment,
    comment_edit_url,
    comment_form_data,
):
    """Пользователь не может редактировать чужой комментарий."""
    old_text = comment.text
    response = reader_client.post(comment_edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
