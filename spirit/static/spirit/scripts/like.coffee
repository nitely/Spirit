###
  Post likes via Ajax
  requires: util.js
###

$ = jQuery


class Like

  defaults:
    csrfToken: "csrf_token",
    likeText: "like ({count})",
    removeLikeText: "remove like ({count})"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    @isSending = false
    do @setUp

  setUp: ->
    @el.on 'click', @sendLike
    @el.on 'click', @stopClick

  sendLike: =>
    if @isSending
      return

    @isSending = true

    post = $.post @el.attr('href'), {csrfmiddlewaretoken: @options.csrfToken, }

    post.done (data) =>
      if data.url_delete
        @addLike data
      else if data.url_create
        @removeLike data
      else
        do @apiError

    post.always =>
      @isSending = false

    return

  addLike: (data) =>
    @el.attr 'href', data.url_delete
    count = @el.data 'count'
    count += 1
    @el.data 'count', count
    removeLikeText = $.format @options.removeLikeText, {count: count, }
    @el.text removeLikeText

  removeLike: (data) =>
    @el.attr 'href', data.url_create
    count = @el.data 'count'
    count -= 1
    @el.data 'count', count
    likeText = $.format @options.likeText, {count: count, }
    @el.text likeText

  apiError: =>
    @el.text "api error"

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.fn.extend
  like: (options) ->
    @each ->
      if not $(@).data 'plugin_like'
        $(@).data 'plugin_like', new Like(@, options)

$.fn.like.Like = Like