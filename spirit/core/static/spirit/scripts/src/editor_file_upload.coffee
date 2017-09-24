###
    Markdown editor image upload, should be loaded before $.editor()
    requires: util.js
###

$ = jQuery


class EditorUpload

    defaults: {
        csrfToken: "csrf_token",
        target: "target url",
        placeholderText: "uploading {name}",
        allowedFileMedia: ["*/*"]
    }
    _meta: {
        fieldName: "file",
        tag: "[{text}]({url})",
        elm: ".js-box-file"
    }

    constructor: (el, options, meta=null) ->
        @el = $(el)  # Editor box
        @options = $.extend({}, @defaults, options)
        @meta = $.extend({}, @_meta, meta or {})
        @formFile = $("<form/>")
        @inputFile = $("<input/>", {
            type: "file",
            accept: @options.allowedFileMedia}).appendTo(@formFile)
        @setUp()

    setUp: ->
        if not window.FormData?
            return

        @inputFile.on('change', @sendFile)

        # TODO: fixme, having multiple editors
        # in the same page would open several
        # dialogs on box-image click
        $boxElm = $(@meta.elm)
        $boxElm.on('click', @openFileDialog)
        $boxElm.on('click', @stopClick)

    sendFile: =>
        file = @inputFile.get(0).files[0]
        placeholder = @addPlaceholder(file)
        formData = @buildFormData(file)

        $.ajax({
            url: @options.target,
            data: formData,
            processData: false,
            contentType: false,
            type: 'POST'
        })
        .done((data) =>
            if "url" of data
                @addFile(data, file, placeholder)
            else
                @addError(data, placeholder)
        )
        .fail((jqxhr, textStatus, error) =>
            @addStatusError(textStatus, error, placeholder)
        )
        .always(() =>
            # Reset the input after uploading,
            # fixes uploading the same image twice
            @formFile.get(0).reset()
        )

        return

    addPlaceholder: (file) =>
        placeholder = $.format(@meta.tag, {
            text: $.format(@options.placeholderText, {name: file.name}),
            url: ""})
        @el.val(@el.val() + placeholder)
        return placeholder

    buildFormData: (file) =>
        formData = new FormData()
        formData.append('csrfmiddlewaretoken', @options.csrfToken)
        formData.append(@meta.fieldName, file)
        return formData

    addFile: (data, file, placeholder) =>
        imageTag = $.format(@meta.tag, {text: file.name, url: data.url})
        @textReplace(placeholder, imageTag)

    addError: (data, placeholder) =>
        error = JSON.stringify(data)
        @textReplace(
            placeholder,
            $.format(@meta.tag, {text: error, url: ""}))

    addStatusError: (textStatus, error, placeholder) =>
        errorTag = $.format(@meta.tag, {
            text: $.format("error: {code} {error}", {
                code: textStatus,
                error: error}),
            url: ""})
        @textReplace(placeholder, errorTag)

    textReplace: (find, replace) =>
        @el.val(@el.val().replace(find, replace))
        return

    openFileDialog: =>
        @inputFile.trigger('click')
        return

    stopClick: (e) ->
        e.preventDefault()
        e.stopPropagation()
        e.stopImmediatePropagation()
        return


$.fn.extend
    editor_file_upload: (options) ->
        @each( ->
            if not $(@).data('plugin_editor_file_upload')
                $(@).data('plugin_editor_file_upload', new EditorUpload(@, options))
        )
    editor_image_upload: (options) ->
        @each( ->
            if not $(@).data('plugin_editor_image_upload')
                $(@).data('plugin_editor_image_upload', new EditorUpload(@, options, {
                    fieldName: "image",
                    tag: "![{text}]({url})",
                    elm: ".js-box-image"
                }))
        )
