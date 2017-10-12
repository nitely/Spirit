###
    Make post on anchor click
###


class Postify

    defaults: {
        csrfToken: "csrf_token"
    }

    constructor: (el, options) ->
        @el = el
        @options = Object.assign({}, @defaults, options)
        @setUp()

    setUp: ->
        @el.addEventListener('click', @makePost)

    makePost: (e) =>
        e.preventDefault()
        e.stopPropagation()

        formElm = document.createElement('form')
        formElm.className = 'js-postify-form'
        formElm.action = @el.getAttribute('href')
        formElm.method = 'POST'
        formElm.style.display = 'none'
        document.body.appendChild(formElm)

        inputCSRFElm = document.createElement('input')
        inputCSRFElm.name = 'csrfmiddlewaretoken'
        inputCSRFElm.type = 'hidden'
        inputCSRFElm.value = @options.csrfToken
        formElm.appendChild(inputCSRFElm)

        formElm.submit()
        return


stModules.postify = (elms, options) ->
    return Array.from(elms).map((elm) -> new Postify(elm, options))

stModules.Postify = Postify
