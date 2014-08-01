#-*- coding: utf-8 -*-

from django.utils.http import urlencode

from .. import register


FACEBOOK_URL = u"http://www.facebook.com/sharer.php?%s"
TWITTER_URL = u"https://twitter.com/share?%s"
GPLUS_URL = u"https://plus.google.com/share?%s"


def _compose_tweet(title):
    # twitter adds the url and a space to the tweet
    # urls, no mather their length, take 23 characters (https)
    extra_len = len(u' ') + 23
    total_len = len(title) + extra_len

    if total_len > 140:
        return title[:(140 - len(u"...") - extra_len)] + u"..."

    return title


@register.simple_tag(takes_context=True)
def get_facebook_share_url(context, url, title):
    request = context['request']
    params = [('u', "100"),
              ('p[url]', request.build_absolute_uri(url)),
              ('p[title]', title)]
    return FACEBOOK_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_twitter_share_url(context, url, title):
    request = context['request']
    url = request.build_absolute_uri(url)
    params = [('url', url),
              ('text', _compose_tweet(title))]
    return TWITTER_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_gplus_share_url(context, url):
    request = context['request']
    params = [('url', request.build_absolute_uri(url)), ]
    return GPLUS_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_email_share_url(context, url, title):
    request = context['request']
    params = [('body', request.build_absolute_uri(url)),
              ('subject', title),
              ('to', "")]
    return u"mailto:?%s" % urlencode(params)


@register.simple_tag(takes_context=True)
def get_share_url(context, url):
    request = context['request']
    return request.build_absolute_uri(url)