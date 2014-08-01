###
  Markdown editor image upload, should be loaded before $.editor()
  requires: util.js
###

$ = jQuery


class EditorImageUpload

  defaults:
    csrfToken: "csrf_token",
    target: "target url",
    placeholderText: "uploading {image_name}"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    @inputFile = $("<input/>", {type: "file", accept: "image/*"})
    do @setUp

  setUp: ->
    if not window.FormData?
      return

    @inputFile.on 'change', @sendFile

    # TODO: fixme, having multiple editors
    # in the same page would open several
    # dialogs on box-image click
    $boxImage = $(".js-box-image")
    $boxImage.on 'click', @openFileDialog
    $boxImage.on 'click', @stopClick

  sendFile: =>
    file = @inputFile.get(0).files[0]
    placeholder = @addPlaceholder file
    formData = @buildFormData file

    post = $.ajax {
      url: @options.target,
      data: formData,
      processData: false,
      contentType: false,
      type: 'POST'
    }

    post.done (data) =>
      if "url" of data
        @addImage data, file, placeholder
      else
        @addError data, placeholder

    post.fail (jqxhr, textStatus, error) =>
      @addStatusError textStatus, error, placeholder

    return

  addPlaceholder: (file) =>
    placeholder = $.format "![#{ @options.placeholderText }]()", {image_name: file.name, }
    @el.val @el.val() + placeholder
    return placeholder

  buildFormData: (file) =>
    formData = new FormData()
    formData.append 'csrfmiddlewaretoken', @options.csrfToken
    formData.append 'image', file
    return formData

  addImage: (data, file, placeholder) =>
    imageTag = $.format "![{name}]({url})", {name: file.name, url: data.url}
    @textReplace placeholder, imageTag

  addError: (data, placeholder) =>
    error = JSON.stringify data
    @textReplace placeholder, "![#{ error }]()"

  addStatusError: (textStatus, error, placeholder) =>
    errorTag = $.format "![error: {code} {error}]()", {code: textStatus, error: error}
    @textReplace placeholder, errorTag

  textReplace: (find, replace) =>
    @el.val @el.val().replace(find, replace)
    return

  openFileDialog: =>
    @inputFile.trigger 'click'
    return

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    do e.stopImmediatePropagation
    return


$.fn.extend
  editor_image_upload: (options) ->
    @each ->
      if not $(@).data 'plugin_editor_image_upload'
        $(@).data 'plugin_editor_image_upload', new EditorImageUpload(@, options)

$.fn.editor_image_upload.EditorImageUpload = EditorImageUpload