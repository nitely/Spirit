###
  A library to tell the server how far you have scrolled down.
  requires: waypoints
###

$ = jQuery


class Mark

  constructor: ->
    @isSending = false
    @commentNumber = do @_getCommentNumber

  _getCommentNumber: ->
    commentNumber = window.location.hash.split("#c")[1]
    commentNumber = parseInt commentNumber, 10  # base 10

    if isNaN commentNumber
      commentNumber = 0
    else
      # workaround to always send comment number from hash
		  commentNumber -= 1

    return commentNumber


class Bookmark

  defaults:
    csrfToken: "csrf_token"
    target: "target url"

  constructor: (el, mark, options) ->
    @el = $(el)
    @mark = mark
    @options = $.extend {}, @defaults, options
    do @setUp

  setUp: ->
    @el.waypoint @onWaypoint, {offset: '100%', }

  onWaypoint: =>
    newCommentNumber = @el.data 'number'

    if newCommentNumber > @mark.commentNumber
      @mark.commentNumber = newCommentNumber
      do @sendCommentNumber

    return

  sendCommentNumber: =>
    if @mark.isSending
      return

    @mark.isSending = true

    post = $.post @options.target, {csrfmiddlewaretoken: @options.csrfToken, comment_number: @mark.commentNumber}
    post.always =>
      @mark.isSending = false


$.fn.extend
  bookmark: (options) ->
    mark = new Mark()

    @each ->
      if not $(@).data 'plugin_bookmark'
        $(@).data 'plugin_bookmark', new Bookmark(@, mark, options)

$.fn.bookmark.Bookmark = Bookmark
$.fn.bookmark.Mark = Mark