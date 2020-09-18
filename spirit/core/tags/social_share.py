# -*- coding: utf-8 -*-

from django.utils.http import urlencode

from .registry import register


FACEBOOK_URL = "https://www.facebook.com/sharer/sharer.php?%s"
TWITTER_URL = "https://twitter.com/share?%s"


def _compose_tweet(title):
    # twitter adds the url and a space to the tweet
    # urls, no mather their length, take 23 characters (https)
    extra_len = len(' ') + 23
    total_len = len(title) + extra_len

    if total_len > 140:
        return title[:(140 - len("...") - extra_len)] + "..."

    return title


@register.simple_tag(takes_context=True)
def get_facebook_share_url(context, url, title):
    request = context['request']
    params = [
        ('u', request.build_absolute_uri(url)),
        ('t', title)]
    return FACEBOOK_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_twitter_share_url(context, url, title):
    request = context['request']
    url = request.build_absolute_uri(url)
    params = [('url', url),
              ('text', _compose_tweet(title))]
    return TWITTER_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_email_share_url(context, url, title):
    request = context['request']
    params = [('body', request.build_absolute_uri(url)),
              ('subject', title),
              ('to', "")]
    return "mailto:?%s" % urlencode(params)


@register.simple_tag(takes_context=True)
def get_share_url(context, url):
    request = context['request']
    return request.build_absolute_uri(url)
