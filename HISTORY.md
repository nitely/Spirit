0.6.2
==================

* Fix password reset
* Make admin user-list redirect to the right
  user profile when clicking on a username

0.6.1
==================

* Update dependencies: `pillow==5.2.0` and `django-djconfig==0.8.0`

0.6.0
==================

* Drops support for Django 1.8, 1.9 and 1.10
* Adds support for Python 3.7 (no changes required)
* Adds support for Django 2.0 and 2.1
* Adds `django.middleware.security.SecurityMiddleware``to
  `MIDDLEWARE_CLASSES` setting
* Adds `LOGOUT_REDIRECT_URL = 'spirit:index'` to settings
* Removes jQuery dependency in favor of vanilla JS
* Fixes user's `last_seen` feature. There was a bug in the middleware
  that would update the field pretty much on every request
* Renames `MIDDLEWARE_CLASSES` (deprecated by django) setting to
  `MIDDLEWARE`
* Removes `spirit.settings` deprecated in Spirit 0.5
* Avoids installing `spirit.topic.poll` app in the generated project
* Updates haystack dependency to 2.8.1

0.5.0
==================

* Drops support for Python 3.3
* Adds support for Python 3.6
* Adds support for Django 1.9, 1.10 and 1.11
* Adds python-magic dependency (to check uploaded files)
* Improvement: focus on comment editor after
  clicking a format button. PR #219 (thanks to @cryptogun)
* Fixes: untranslated strings. PR #218 (thanks to @cryptogun)
* Fixes: missing link on admin flag. PR #217 (thanks to @cryptogun)
* Fixes: `XForwardedForMiddleware` middleware and
  gunicorn error. PR #216 (thanks to @cryptogun)
* Improvement: Add `@username` on comment editor
  when clicking on a reply link. PR #212 (thanks to @cryptogun)
* Improvement: notifications page drop-down
  menu for read/unread. PR #213 (thanks to @cryptogun)
* New: lithuanian translation, thanks to @sirex
* New: file upload on comments
* Improvement: Adds `ST_UPLOAD_IMAGE_ENABLED`
  to enable/disable image uploads and `ST_UPLOAD_FILE_ENABLED`
  to enable/disable file uploads
* Remove deprecated `topic_poll` app
* Remove deprecated (since v0.2) `spirit_user.User` (PR #141),
  read the wiki or the PR for a workaround
* Updates mistune, haystack and woosh dependencies
* Deprecates `spirit.settings`. It will be removed in future releases
* Updates locales

0.4.8
==================

* New: Anti double post (including comments, topics and private topics)
* New: Adds `ST_DOUBLE_POST_THRESHOLD_MINUTES` setting to change the
  the threshold time in which the double posting is prevented
* Improvement: Adds `ST_COMMENT_MAX_LEN` setting to change
  the maximum characters limit per comment (#107)
* New: Adds optional category title color (#110 thanks to @sheepsy90)
* Fix: `Too many submissions` when form submission has an error (#58)
* New: Key based expiration rate-limit.
* New: `ST_RATELIMIT_CACHE = 'st_rate_limit'` setting and `CACHE`.
* Fix: Boolean filters for Elasticsearch (PR #130)
* Improvement: UTC timezones instead of GMT in user profile form (#108)
* Fix: missing emojis (#93)
* Improvement: Replaced twitter emoji pack by emojiOne pack (PR #126)
* Improvement: Search within comments (#57)
* Improvement: Search-index partial update (PR #129)
* Improvement: Support for YouTube embeds that have a
  timestamp (PR #116 thanks to @alesdotio)

0.4.7
==================

* Removed unused `ST_UNCATEGORIZED_CATEGORY_PK` setting
* Security fix: fixes a regression within markdown
URLs present in v0.4.6 (#105 thanks to @qll)
* New: `settings.ST_ALLOWED_URL_PROTOCOLS` a set containing valid URL protocols

0.4.6
==================

* Improvement: Updated mistune (markdown) dependency
* Fix: Facebook share link (#87 thanks to @initialkommit)
* Improvement: Adds email confirmation in registration
* Improvement: Removes password confirmation in registration
* Improvement: Login message changed to inform when the username is not found
* Improvement: Force HTML5 youtube player

0.4.5
==================

* Adds Python 3.5 support
* New: Comment history diff (inserted & deleted lines)
* New: Twitter emojis pack
* New (Dev): Gulp tasks `npm run gulp css` and `npm run gulp coffee` for building assets
* Improvement: Adds `rel="nofollow"` to all comment links of regular users
* Improvement: CSS & JS minification and concatenation
* Improvement: Added `STATICFILES_STORAGE = 'ManifestStaticFilesStorage'` (settings.prod only) to
append hashes to assets file names
* Improvement: `woff2` font support
* Fix: Email required on registration
* Fix: Changed `DEFAULT_FROM_EMAIL` default to `webmaster@localhost` (Django's default)
* Fix: Redirect to first unread comment on visited topics
* Fix: Adds missing `apps.AppConfig` in `spirit.search` to avoid app label clashes.

0.4.4
==================

* New: mark topic as visited (grey out the link) when it has a bookmark
* New: mark topic as *has new comments* (red out comment icon) when it has new comments
* Fix: send emails as `DEFAULT_FROM_EMAIL` (default to `site.name <noreply@[site.domain]>`),
setting this will be mandatory in future releases (default will be removed).
* Fix: Implement missing `apps.AppConfig` in `spirit.core` to avoid app label clashes.
* Fix: Show category names in the advance search template.

0.4.3
==================

* New app comment.poll: Polls within comments
* New: Floating flash messages when there is a hash in the URL
* New: Case insensitive emails (setting.ST_CASE_INSENSITIVE_EMAILS)
* New & updated translations: Turkish (thanks to negativefix), Hungarian (thanks to istvanf),
Polish, Polish (Poland), Spanish, German, Chinese, Swedish and Russian

0.4.2
==================

* Adds management commands: spiritinstall, spiritupgrade
* Fix to use current date when a history comment is created

0.4.1
==================

* Adds missing user profile migration (issue #62)

0.4.0
==================

* Removed old migrations.
* Removed `spirit` app, it has been decoupled into many apps.

0.3.0
==================

* Requires Django 1.8 (support for 1.7 has been dropped).
* Drops the custom `AUTH_USER_MODEL`.
* Deprecated `AbstractForumUser` and `AbstractUser`. They will be removed in future releases.
* Moved `spirit.middleware.XForwardedForMiddleware` to `spirit.core.middleware.XForwardedForMiddleware`.
* Moved `spirit.middleware.TimezoneMiddleware` to `spirit.user.middleware.TimezoneMiddleware`.
* Moved `spirit.middleware.LastIPMiddleware` to `spirit.user.middleware.LastIPMiddleware`.
* Moved `spirit.middleware.LastSeenMiddleware` to `spirit.user.middleware.LastSeenMiddleware`.
* Moved `spirit.middleware.ActiveUserMiddleware` to `spirit.user.middleware.ActiveUserMiddleware`.
* Moved `spirit.middleware.PrivateForumMiddleware` to `spirit.core.middleware.PrivateForumMiddleware`.
* Removed most signals.
* Renamed models: `spirit.Category` to `spirit_category.category`, `spirit.UserProfile` to `spirit_user.UserProfile`, `spirit.Topic` to `spirit_topic.Topic`, `spirit.TopicFavorite` to `spirit_topic_favorite.TopicFavorite`, `spirit.Comment` to `spirit_comment.Comment`, `spirit.TopicNotification` to `spirit_topic_notification.TopicNotification`, `spirit.TopicPoll` to `spirit_topic_poll.TopicPoll`, `spirit.TopicPollChoice` to `spirit_topic_poll.TopicPollChoice`, `spirit.TopicPollVote` to `spirit_topic_poll.TopicPollVote`, `spirit.TopicPrivate` to `spirit_topic_private.TopicPrivate`, `spirit.TopicUnread` to `spirit_topic_unread.TopicUnread`, `spirit.CommentBookmark` to `spirit_comment_bookmark.CommentBookmark`, `spirit.CommentFlag` to `spirit_comment_flag.CommentFlag`, `spirit.Flag` to `spirit_comment_flag.Flag`, `spirit.CommentHistory` to `spirit_comment_history.CommentHistory` and `spirit.CommentLike` to `spirit_comment_like.CommentLike`. `ContentTypes` were renamed accordingly, so if you have a model that relates to Spirit via a GenericForeignKey, you should not worry about it.

0.2.0
==================

* Requires Django 1.7 (support for 1.6 has been dropped).
* Polls.
* Better markdown parser.
* Global pinned topics and regular pinned topics.
* Unicode url slug.

0.1.3
==================

* Swappable user model: allows you to replace the Spirit user model by your own user model.

0.1.2
==================

* Code highlighting.
* Emojis popup selector.
* Js scripts rewritten in coffeescript + tests.
* Social Integration: share comments on twitter, etc.
* Languages: German (by derWalter), Swedish (by silverstream).

0.1.1
==================

* Private forum setting: if it's on, it won't allow non-members to browse the forum.
* Markdown fenced code blocks.
* Image upload for comments (not Drag&Drop).
