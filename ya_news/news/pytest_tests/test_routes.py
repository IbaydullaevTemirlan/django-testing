from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        lf('home_url'),
        lf('detail_url'),
        lf('login_url'),
        lf('signup_url'),
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """Главная/детальная/логин/регистрация доступны анонимному пользователю."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client, logout_url):
    """Логаут доступен анонимному пользователю (POST-запросом)."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        lf('comment_edit_url'),
        lf('comment_delete_url'),
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    url,
    expected_status,
):
    """Редактирование/удаление: автору OK, не автору 404."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        lf('comment_edit_url'),
        lf('comment_delete_url'),
    ),
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """Аноним перенаправляется на логин при попытке редактировать/удалять."""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
