#-*- coding: utf-8 -*-


def quotify(comment, username):
    """
    Converts 'Foo\nbar' to:
    @username
    > Foo
    > bar
    \n\n
    """
    header = u"@%s" % username
    lines = comment.splitlines()
    quote = u"\n> ".join(lines)
    quote = u"%(header)s\n> %(quote)s\n\n" % ({'header': header, 'quote': quote})
    return quote