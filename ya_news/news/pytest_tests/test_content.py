from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, many_news, home_url):
    """На главной странице не больше NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news, home_url):
    """Новости на главной отсортированы от свежих к старым."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, news_with_comments, detail_url):
    """Комментарии отсортированы от старых к новым."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """Анониму не передаётся форма комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Авторизованному передаётся форма комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
