# -*- coding: utf-8 -*-

"""
These are the default settings. \
They can be overridden by the project settings
"""

from __future__ import unicode_literals
import os

#: The category's PK containing all of the private topics.
#: The category is auto-created and so this value should not change
ST_TOPIC_PRIVATE_CATEGORY_PK = 1

#: Enable/disable the rate-limit for all forms
ST_RATELIMIT_ENABLE = True
#: The cache key prefix. This is mostly to avoid clashing with other apps
ST_RATELIMIT_CACHE_PREFIX = 'srl'
#: The cache ID for storing rate-limit related data.
#: The cache ID must be a valid ``CACHES`` entry and
#: the ``TIMEOUT`` must be ``None`` otherwise it will misbehave
ST_RATELIMIT_CACHE = 'st_rate_limit'
#: A warning will be printed when the ``TIMEOUT``
#: is not ``None``. Setting this to ``True`` will silence it.
#:
#: .. Warning:: A ``ConfigurationError`` will be raised instead of a warning in Spirit > 0.5
ST_RATELIMIT_SKIP_TIMEOUT_CHECK = False

#: Number of notifications per page
ST_NOTIFICATIONS_PER_PAGE = 20

#: Maximum length for a comment
ST_COMMENT_MAX_LEN = 3000
#: Maximum number of mentions per comment willing to process
ST_MENTIONS_PER_COMMENT = 30
#: Minutes to wait before a given user
#: will be able to post a duplicated comment/topic
ST_DOUBLE_POST_THRESHOLD_MINUTES = 30

#: Number of next/previous pages the paginator will show
ST_YT_PAGINATOR_PAGE_RANGE = 3

#: Minimum length for a given search query
ST_SEARCH_QUERY_MIN_LEN = 3

#: Threshold in minutes before the user
#: `"last seen"` info can be updated
ST_USER_LAST_SEEN_THRESHOLD_MINUTES = 1

#: Settings this to ``True`` will require
#: all users to be logged-in to access any section
ST_PRIVATE_FORUM = False

#: Enable/disable image uploads within posts
ST_UPLOAD_IMAGE_ENABLED = True
#: Uploaded images will be validated against these formats.
#: Also, the file choosing dialog will filter by these extensions.
#: See the `Pillow docs <http://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html>`_
#: for a list of supported formats
#:
#: .. Warning::
#:     Allowing PNG files is a security risk as it may contain malicious HTML.
#:     See `Django notes <https://docs.djangoproject.com/en/1.11/topics/security/#user-uploaded-content>`_
ST_ALLOWED_UPLOAD_IMAGE_FORMAT = ('jpeg', 'jpg', 'gif')

#: Enable/disable file uploads within posts.
#: Requires running ``pip install django-spirit[files]`` to install
#: `python-magic <https://github.com/ahupp/python-magic#installation>`_
ST_UPLOAD_FILE_ENABLED = False
#: Uploaded files will be validated against these formats.
#: This is a map of extension and media-type. Both are used for validation
#:
#: .. Note::
#:     To find a media-type just add an extension and an empty media-type,
#:     then try uploading a valid file for that extension and the expected
#:     media-type will be printed within the validation error.
#:     Either that or use the Linux ``file --mime-type ./my_file`` command
ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE = {
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pdf': 'application/pdf'}

#: Link protocols allowed within posts
ST_ALLOWED_URL_PROTOCOLS = {
    'http', 'https', 'mailto', 'ftp', 'ftps',
    'git', 'svn', 'magnet', 'irc', 'ircs'}

#: Support unicode slugs. Set to ``False``
#: to only allow ASCII chars
ST_UNICODE_SLUGS = True

#: Reject duplicated emails when creating a new account
ST_UNIQUE_EMAILS = True
#: Make emails case insensitive
ST_CASE_INSENSITIVE_EMAILS = True

# Tests helper
ST_TESTS_RATELIMIT_NEVER_EXPIRE = False

# Full route to the spirit package
ST_BASE_DIR = (
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))
