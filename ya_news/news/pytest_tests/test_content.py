from datetime import date, timedelta

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(client):
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 3):
        News.objects.create(title=f'Title {i}', text='Text')

    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date_desc(client):
    today = date.today()
    n1 = News.objects.create(title='n1', text='t', date=today)
    n2 = News.objects.create(
        title='n2',
        text='t',
        date=today - timedelta(days=1),
    )
    n3 = News.objects.create(
        title='n3',
        text='t',
        date=today - timedelta(days=2),
    )

    response = client.get(reverse('news:home'))
    object_list = list(response.context['object_list'])

    assert object_list[:3] == [n1, n2, n3]
    dates = [n.date for n in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_sorted_by_created_asc(client, author, news):
    Comment.objects.create(news=news, author=author, text='First')
    Comment.objects.create(news=news, author=author, text='Second')

    response = client.get(reverse('news:detail', args=(news.id,)))
    news_obj = response.context['news']
    comments = list(news_obj.comment_set.all())

    created_list = [c.created for c in comments]
    assert created_list == sorted(created_list)


def test_anonymous_has_no_comment_form(client, news):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


def test_authorized_has_comment_form(author_client, news):
    response = author_client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
