###
  Markdown editor
  requires: marked.js
###

$ = jQuery


class Editor

  defaults:
    boldedText: "bolded text",
    italicisedText: "italicised text",
    listItemText: "list item",
    linkText: "link text",
    linkUrlText: "link url",
    imageText: "image text",
    imageUrlText: "image url"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    do @setUp

  setUp: ->
    # TODO: fixme, having multiple editor
    # in the same page will trigger button
    # click on every editor
    $('.js-box-bold').on 'click', @addBold
    $('.js-box-italic').on 'click', @addItalic
    $('.js-box-list').on 'click', @addList
    $('.js-box-url').on 'click', @addUrl
    $('.js-box-image').on 'click', @addImage
    $('.js-box-preview').on 'click', @togglePreview

  wrapSelection: (preTxt, postTxt, defaultTxt) =>
    preSelection = @el.val().substring 0, @el[0].selectionStart
    selection = @el.val().substring @el[0].selectionStart, @el[0].selectionEnd
    postSelection = @el.val().substring @el[0].selectionEnd

    if not selection
      selection = defaultTxt

    @el.val preSelection + preTxt + selection + postTxt + postSelection

  addBold: =>
    @wrapSelection "**", "**", @options.boldedText
    return false

  addItalic: =>
    @wrapSelection "*", "*", @options.italicisedText
    return false

  addList: =>
    @wrapSelection "\n* ", "", @options.listItemText
    return false

  addUrl: =>
    @wrapSelection "[", "](#{ @options.linkUrlText })", @options.linkText
    return false

  addImage: =>
    @wrapSelection "![", "](#{ @options.imageUrlText })", @options.imageText
    return false

  togglePreview: =>
    $preview = $('.js-box-preview-content')

    do @el.toggle
    do $preview.toggle
    $preview.html marked @el.val()

    return false


$.fn.extend
  editor: (options) ->
    @each ->
      if not $(@).data 'plugin_editor'
        $(@).data 'plugin_editor', new Editor(@, options)

$.fn.editor.Editor = Editor