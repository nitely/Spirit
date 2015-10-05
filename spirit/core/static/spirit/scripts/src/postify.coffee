###
  Make post on anchor click
###

$ = jQuery


class Postify

  defaults:
    csrfToken: "csrf_token"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    do @setUp

  setUp: ->
    @el.on 'click', @makePost
    @el.on 'click', @stopClick

  makePost: =>
    $form = $("<form/>", {
      action: @el.attr('href'),
      method: "post"
    }).hide().appendTo $('body')

    # inputCsrfToken
    $("<input/>", {
      name: "csrfmiddlewaretoken",
      type: "hidden",
      value: @options.csrfToken
    }).appendTo $form

    @formSubmit $form

    return

  formSubmit: ($form) ->
    do $form.submit

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.fn.extend
  postify: (options) ->
    @each ->
      if not $(@).data 'plugin_postify'
        $(@).data 'plugin_postify', new Postify(@, options)

$.fn.postify.Postify = Postify