###
  Move comments to other topic
###

$ = jQuery


class MoveComment
  #TODO: prefix classes with js-

  defaults:
    csrfToken: "csrf_token",
    target: "#post_url"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    do @setUp

  setUp: ->
    @el.on 'click', @showMoveComments
    @el.on 'click', @stopClick

    # TODO: this should probably be moved from
    # here to its own class, since it gets
    # called for every el. Since we have only
    # one "move comments" link, it's ok for now.
    $move_comments = $(".js-move-comments")
    $move_comments.on 'click', @moveComments
    $move_comments.on 'click', @stopClick

  showMoveComments: =>
    if $(".move-comments").is ":hidden"
      do $(".move-comments").show
      do @addCommentSelection

    return

  addCommentSelection: =>
    $li = $("<li/>").appendTo ".comment-date"

    $checkbox = $("<input/>", {
      class: "move-comment-checkbox",
      name: "comments",
      type: "checkbox",
      value: ""
    }).appendTo $li

    # add comment_id to every checkbox value
    $checkbox.each ->
      $commentId = $(@).closest(".comment").data "pk"
      $(@).val $commentId

  moveComments: =>
    $form = $("<form/>", {
      action: @options.target,
      method: "post"
    }).hide().appendTo $('body')

    # inputCsrfToken
    $("<input/>", {
      name: "csrfmiddlewaretoken",
      type: "hidden",
      value: @options.csrfToken
    }).appendTo $form

    # inputTopicId
    topicId = $("#id_move_comments_topic").val()
    $("<input/>", {
      name: "topic",
      type: "text",
      value: topicId
    }).appendTo $form

    # append all selection inputs
    $(".move-comment-checkbox").clone().appendTo $form

    @formSubmit $form

    return

  formSubmit: ($form) ->
    do $form.submit

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.fn.extend
  move_comments: (options) ->
    @each ->
      if not $(@).data 'plugin_move_comments'
        $(@).data 'plugin_move_comments', new MoveComment(@, options)

$.fn.move_comments.MoveComment = MoveComment