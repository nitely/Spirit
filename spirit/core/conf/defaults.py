# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

ST_TOPIC_PRIVATE_CATEGORY_PK = 1

ST_RATELIMIT_ENABLE = True
ST_RATELIMIT_CACHE_PREFIX = 'srl'
ST_RATELIMIT_CACHE = 'default'
ST_RATELIMIT_SKIP_TIMEOUT_CHECK = False

ST_NOTIFICATIONS_PER_PAGE = 20

ST_COMMENT_MAX_LEN = 3000
ST_MENTIONS_PER_COMMENT = 30
ST_DOUBLE_POST_THRESHOLD_MINUTES = 30

ST_YT_PAGINATOR_PAGE_RANGE = 3

ST_SEARCH_QUERY_MIN_LEN = 3

ST_USER_LAST_SEEN_THRESHOLD_MINUTES = 1

ST_PRIVATE_FORUM = False

# PNG is not allowed by default due to:
# An HTML file can be uploaded as an image
# if that file contains a valid PNG header
# followed by malicious HTML. See:
# https://docs.djangoproject.com/en/1.11/topics/security/#user-uploaded-content
ST_ALLOWED_UPLOAD_IMAGE_FORMAT = ('jpeg', 'gif')
ST_ALLOWED_URL_PROTOCOLS = {
    'http', 'https', 'mailto', 'ftp', 'ftps',
    'git', 'svn', 'magnet', 'irc', 'ircs'}

ST_UNICODE_SLUGS = True

ST_UNIQUE_EMAILS = True
ST_CASE_INSENSITIVE_EMAILS = True

# Tests helpers
ST_TESTS_RATELIMIT_NEVER_EXPIRE = False

# Full route to the spirit package
ST_BASE_DIR = (
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))
