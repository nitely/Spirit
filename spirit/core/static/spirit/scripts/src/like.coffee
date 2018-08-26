###
    Post likes via Ajax
    requires: modules, util.js
###

utils = stModules.utils


class Like

    defaults: {
        csrfToken: "csrf_token",
        likeText: "like ({count})",
        removeLikeText: "remove like ({count})"
    }

    constructor: (el, options) ->
        @el = el
        @options = Object.assign({}, @defaults, options)
        @isSending = false
        @setUp()

    setUp: ->
        @el.addEventListener('click', @sendLike)

    sendLike: (e) =>
        e.preventDefault()
        e.stopPropagation()

        if @isSending
            return

        @isSending = true

        formData = new FormData()
        formData.append('csrfmiddlewaretoken', @options.csrfToken)
        headers = new Headers()
        headers.append("X-Requested-With", "XMLHttpRequest")

        fetch(@el.getAttribute('href'), {
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
            if data.url_delete
                @addLike(data.url_delete)
            else if data.url_create
                @removeLike(data.url_create)
            else
                @apiError()
        )
        .catch((error) =>
            console.log(error.message)
            @apiError()
        )
        .then( =>
            @isSending = false
        )

        return

    addLike: (urlDelete) =>
        @el.setAttribute('href', urlDelete)
        @el.dataset.count = String(parseInt(@el.dataset.count, 10) + 1)
        @el.innerHTML = utils.format(@options.removeLikeText, {count: @el.dataset.count})

    removeLike: (urlCreate) =>
        @el.setAttribute('href', urlCreate)
        @el.dataset.count = String(parseInt(@el.dataset.count, 10) - 1)
        @el.innerHTML = utils.format(@options.likeText, {count: @el.dataset.count})

    apiError: =>
        @el.textContent = "api error"


stModules.like = (elms, options) ->
    return Array.from(elms).map((elm) -> new Like(elm, options))

stModules.Like = Like
