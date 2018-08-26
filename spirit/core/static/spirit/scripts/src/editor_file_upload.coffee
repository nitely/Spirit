###
    Markdown editor image upload, should be loaded before $.editor()
    requires: util.js
###

utils = stModules.utils


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

    constructor: (el, options=null, meta=null) ->
        @el = el
        @options = Object.assign({}, @defaults, options or {})
        @meta = Object.assign({}, @_meta, meta or {})
        @textBox = el.querySelector('textarea')
        @formFile = document.createElement('form')
        @inputFile = document.createElement('input')
        @inputFile.type = "file"
        @inputFile.accept = @options.allowedFileMedia
        @setUp()

    setUp: ->
        @formFile.appendChild(@inputFile)
        @inputFile.addEventListener('change', @sendFile)
        @el.querySelector(@meta.elm).addEventListener('click', @openFileDialog)

    sendFile: =>
        # todo: allow many files
        file = @inputFile.files[0]
        placeholder = @addPlaceholder(file)
        formData = @buildFormData(file)

        # Reset the input fixes uploading the same image twice
        @formFile.reset()

        headers = new Headers()
        headers.append("X-Requested-With", "XMLHttpRequest")

        fetch(@options.target, {
            method: "POST",
            headers: headers,
            credentials: 'same-origin',
            body: formData
        })
        .then((response) =>
            if not response.ok
                throw new Error("error: #{response.status} #{response.statusText}")

            return response.json()  # Promise
        )
        .then((data) =>
            if "url" of data
                @addFile(file.name, data.url, placeholder)
            else
                @addError(JSON.stringify(data.error), placeholder)
        )
        .catch((error) =>
            console.log(error.message)
            @addError(error.message, placeholder)
        )

        return

    addPlaceholder: (file) =>
        placeholder = utils.format(@meta.tag, {
            text: utils.format(@options.placeholderText, {name: file.name}),
            url: ""})
        # todo: add at current pointer position
        @textBox.value += placeholder
        return placeholder

    buildFormData: (file) =>
        formData = new FormData()
        formData.append('csrfmiddlewaretoken', @options.csrfToken)
        formData.append(@meta.fieldName, file)
        return formData

    addFile: (name, url, placeholder) =>
        imageTag = utils.format(@meta.tag, {text: name, url: url})
        @textReplace(placeholder, imageTag)

    addError: (error, placeholder) =>
        @textReplace(
            placeholder,
            utils.format(@meta.tag, {text: error, url: ""}))

    textReplace: (find, replace) =>
        # todo: put current pointer position back
        @textBox.value = @textBox.value.replace(find, replace)
        return

    openFileDialog: (e) =>
        e.preventDefault()
        e.stopPropagation()
        # Avoid default editor button-click handler
        e.stopImmediatePropagation()
        @inputFile.click()


stModules.editorFileUpload = (elms, options) ->
    return Array.from(elms).map((elm) -> new EditorUpload(elm, options))

stModules.editorImageUpload = (elms, options) ->
    return Array.from(elms).map((elm) -> new EditorUpload(elm, options, {
        fieldName: "image",
        tag: "![{text}]({url})",
        elm: ".js-box-image"
    }))

stModules.EditorUpload = EditorUpload
