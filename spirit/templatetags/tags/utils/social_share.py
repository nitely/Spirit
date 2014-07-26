#-*- coding: utf-8 -*-

from urllib import urlencode

from .. import register


FACEBOOK_URL = u"http://www.facebook.com/sharer.php?%s"
TWITTER_URL = u"https://twitter.com/share?%s"
GPLUS_URL = u"https://plus.google.com/share?%s"


def _compose_tweet(title, url):
    # twitter adds the url and a space to the tweet
    extra_len = len(' ') + len(url)
    total_len = len(title) + extra_len

    if total_len > 140:
        return title[:(140 - len("…") - extra_len)] + "…"

    return title


@register.simple_tag(takes_context=True)
def get_facebook_share_url(context, url, title):
    request = context['request']
    params = {'u': "100",
              'p[url]': request.build_absolute_uri(url),
              'p[title]': title}
    return FACEBOOK_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_twitter_share_url(context, url, title):
    request = context['request']
    url = request.build_absolute_uri(url)
    params = {'url': url,
              'text': _compose_tweet(title, url)}
    return TWITTER_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_twitter_share_url(context, url, title):
    request = context['request']
    url = request.build_absolute_uri(url)
    params = {'url': url,
              'text': _compose_tweet(title, url)}
    return TWITTER_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_gplus_share_url(context, url):
    request = context['request']
    params = {'url': request.build_absolute_uri(url), }
    return GPLUS_URL % urlencode(params)


@register.simple_tag(takes_context=True)
def get_email_share_url(context, url, title):
    request = context['request']
    params = {'body': request.build_absolute_uri(url),
              'subject': title,
              'to': ""}
    return u"mailto:?%s" % urlencode(params)


@register.simple_tag(takes_context=True)
def get_share_url(context, url):
    request = context['request']
    return request.build_absolute_uri(url)