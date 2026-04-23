import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, many_news):
    """Количество новостей на главной странице - не более заданного в настройках."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    """Новости на главной странице отсортированы от свежих к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_with_comments):
    """Комментарии на странице новости отсортированы от старых к новым."""
    url = reverse('news:detail', args=(news_with_comments.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)