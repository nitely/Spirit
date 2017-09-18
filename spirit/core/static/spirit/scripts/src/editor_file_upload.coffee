###
    Markdown editor image upload, should be loaded before $.editor()
    requires: util.js
###

$ = jQuery


class EditorFileUpload

    defaults: {
        csrfToken: "csrf_token",
        target: "target url",
        placeholderText: "uploading {file_name}"
    }

    constructor: (el, options) ->
        @el = $(el)
        @options = $.extend({}, @defaults, options)
        @formFile = $("<form/>")
        @inputFile = $("<input/>", {
            type: "file",
            accept: ".doc, .docx, .pdf"}).appendTo(@formFile)
        @setUp()

    setUp: ->
        if not window.FormData?
            return

        @inputFile.on('change', @sendFile)

        # TODO: fixme, having multiple editors
        # in the same page would open several
        # dialogs on box-image click
        $boxImage = $(".js-box-file")
        $boxImage.on('click', @openFileDialog)
        $boxImage.on('click', @stopClick)

    sendFile: =>
        file = @inputFile.get(0).files[0]
        placeholder = @addPlaceholder(file)
        formData = @buildFormData(file)

        post = $.ajax({
            url: @options.target,
            data: formData,
            processData: false,
            contentType: false,
            type: 'POST'
        })

        post.done((data) =>
            if "url" of data
                @addFile(data, file, placeholder)
            else
                @addError(data, placeholder)
        )

        post.fail((jqxhr, textStatus, error) =>
            @addStatusError(textStatus, error, placeholder)
        )

        post.always(() =>
            # Reset the input after uploading,
            # fixes uploading the same image twice
            @formFile.get(0).reset()
        )

        return

    addPlaceholder: (file) =>
        placeholder = $.format("[#{ @options.placeholderText }]()", {file_name: file.name, })
        @el.val(@el.val() + placeholder)
        return placeholder

    buildFormData: (file) =>
        formData = new FormData()
        formData.append('csrfmiddlewaretoken', @options.csrfToken)
        formData.append('file', file)
        return formData

    addFile: (data, file, placeholder) =>
        # format as a link to the file
        fileTag = $.format("[{name}]({url})", {name: file.name, url: data.url})
        @textReplace(placeholder, fileTag)

    addError: (data, placeholder) =>
        error = JSON.stringify(data)
        @textReplace(placeholder, "[#{ error }]()")

    addStatusError: (textStatus, error, placeholder) =>
        errorTag = $.format("[error: {code} {error}]()", {code: textStatus, error: error})
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
                $(@).data('plugin_editor_file_upload', new EditorFileUpload(@, options))
        )

$.fn.editor_file_upload.EditorFileUpload = EditorFileUpload
