# -*- coding: utf-8 -*-

"""
These are the default settings. \
They can be overridden by the project settings
"""

import os

#: The forum URL, ex: ``"https://community.spirit-project.com/"``.
#: This is used to construct the links in the emails: email verification,
#: password reset, notifications, etc. A ``ImproperlyConfigured`` error
#: is raised if this is not set.
ST_SITE_URL = None

#: The media file storage for Spirit.
#: The default file storage is used if this
#: is not set. In either case, the storage should
#: be set to overwrite files. Otherwise, files such
#: as user avatar changes will waste space. Other uploaded
#: files/images have a unique path so they are never overwritten.
#: Changing this value will create a pointless
#: DB migration in ``Django < 3.1``
ST_STORAGE = None

#: The task manager to run delayed and periodic tasks
#: such as send emails, update the search index, clean up django
#: sessions, etc. Valid values are: ``'celery'``, ``'huey'``, and
#: ``None``. Requires running ``pip install django-spirit[huey]``
#: to install Huey, and ``pip install django-spirit[celery]`` to
#: install Celery
ST_TASK_MANAGER = None

#: Tasks schedule for the Huey task manager.
#: It contains a dict of tasks, and every
#: task a dict of crontab params. Beware, the
#: default value for every missing param is ``'*'``.
#: See `Huey periodic tasks <https://huey.readthedocs.io/en/latest/guide.html#periodic-tasks>`_
ST_HUEY_SCHEDULE = {
    'full_search_index_update': {
        'minute': '0',
        'hour': '*/24'
    },
    'notify_weekly': {
        'minute': '0',
        'hour': '0',
        'day_of_week': '1'  # 0=Sunday, 6=Saturday
    }
}

#: Default email notification
#: frequency. This is applied to new users;
#: existing users will default to ``'never'``.
#: Valid values are ``'never'``, ``'immediately'``,
#: and ``'weekly'``
ST_NOTIFY_WHEN = 'never'

#: | The age in hours of the items
#:   to index into the search index on each update.
#: | The update is run by a periodic task; ex:
#:   ``ST_HUEY_SCHEDULE['full_search_index_update']``
#:   in case of Huey.
#: | The task schedule for the selected ``ST_TASK_MANAGER``
#:   will need to be set to this value (or lesser)
ST_SEARCH_INDEX_UPDATE_HOURS = 24

#: The category's PK containing all of the private topics.
#: The category is auto-created and so this value should not change
ST_TOPIC_PRIVATE_CATEGORY_PK = 1
#: Enable/disable category ordering.
ST_ORDERED_CATEGORIES = False

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
#: Truncate displayed URL in comments
# if it's longer than this number of characters
ST_COMMENT_MAX_URL_LEN = 30
#: Maximum number of mentions per comment willing to process
ST_MENTIONS_PER_COMMENT = 30
#: Minutes to wait before a given user
#: will be able to post a duplicated comment/topic
ST_DOUBLE_POST_THRESHOLD_MINUTES = 30
#: Enable MathJax. Spirit's markdown supports
#: math notation with ``$$...$$``, ``\(...\)``, ``\[...\]``
#: and ``\begin{abc}...\end{abc}``, this merely insert the
#: MathJax script into the HTML.
ST_MATH_JAX = False

#: Number of next/previous pages the paginator will show
ST_YT_PAGINATOR_PAGE_RANGE = 3

#: Minimum length for a given search query
ST_SEARCH_QUERY_MIN_LEN = 3

#: Threshold in minutes before the user
#: `"last seen"` info can be updated
ST_USER_LAST_SEEN_THRESHOLD_MINUTES = 1

#: The user avatar will be validated against these formats.
#: See the `Pillow docs <http://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html>`_
#: for a list of supported formats
#:
#: .. Warning::
#:     Allowing PNG files is a security risk as it may contain malicious HTML.
#:     See `Django notes <https://docs.djangoproject.com/en/1.11/topics/security/#user-uploaded-content>`_
ST_ALLOWED_AVATAR_FORMAT = ('jpeg', 'jpg')

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

#: Make user-names case insensitive
#:
#: .. Note::
#:     This can be set to ``False`` at any time,
#:     however setting it back to ``True`` requires
#:     taking care of clashing users,
#:     i.e: ``someuser``, ``SomeUser`` and ``SoMeUsEr``,
#:     only one of those users will be able log-in
#:     (the one in lowercase). Removing clashing users
#:     is usually not possible.
ST_CASE_INSENSITIVE_USERNAMES = True

#: Prevent duplication of files
#: uploaded by a user. Including images.
#: This is not across
#: all users, but a single user.
#:
#: Be aware the de-duplication is based on
#: a file hash calculation, which is
#: quite slow and it will degrade the server's
#: performance.
#:
#: All files will have the hash as name and
#: the original file's name will be lost.
#:
#: .. Note::
#:     Defaults to ``False`` since Spirit 0.8
ST_PREVENT_SOME_FILE_DUPLICATION = False

#: Use the extended font variation. Includes
#: Latin, Greek, and Cyrillic charsets
ST_EXTENDED_FONT = False

# Tests helper
ST_TESTS_RATELIMIT_NEVER_EXPIRE = False

# Full route to the spirit package
ST_BASE_DIR = (
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))
