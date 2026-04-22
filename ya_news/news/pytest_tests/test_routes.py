import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_available_for_anonymous(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


def test_detail_available_for_anonymous(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_delete_available_for_author(author_client, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    assert author_client.get(edit_url).status_code == 200
    assert author_client.get(delete_url).status_code == 200


def test_comment_edit_delete_redirect_for_anonymous(client, comment):
    login_url = reverse('users:login')
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    response = client.get(edit_url)
    assert response.status_code == 302
    assert response.url == f'{login_url}?next={edit_url}'

    response = client.get(delete_url)
    assert response.status_code == 302
    assert response.url == f'{login_url}?next={delete_url}'


def test_comment_edit_delete_404_for_not_author(reader_client, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    assert reader_client.get(edit_url).status_code == 404
    assert reader_client.get(delete_url).status_code == 404


def test_auth_pages_available_for_anonymous(client):
    signup_url = reverse('users:signup')
    login_url = reverse('users:login')
    logout_url = reverse('users:logout')

    response = client.get(signup_url)
    assert response.status_code == 200

    response = client.get(login_url)
    assert response.status_code == 200

    response = client.get(logout_url)
    assert response.status_code in (200, 405)

    if response.status_code == 405:
        response = client.post(logout_url)
        assert response.status_code in (200, 302)
