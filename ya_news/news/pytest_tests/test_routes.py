from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Публичные страницы доступны анониму (logout проверяем POST-запросом)."""
    url = reverse(name, args=args)
    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code == HTTPStatus.OK
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
    parametrized_client,
    name,
    comment_args,
    expected_status,
):
    """Редакт./удал.: автору OK, не автору 404."""
    url = reverse(name, args=comment_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirects(client, name, comment_args):
    """Аноним перенаправляется на логин при редактировании/удалении."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
