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
        if @isSending
            return

        @isSending = true

        formData = new FormData()
        formData.append('csrfmiddlewaretoken', @options.csrfToken)
        headers = new Headers()
        headers.append("X-Requested-With", "XMLHttpRequest")

        fetch(@el.href, {
            method: "POST",
            headers: headers,
            credentials: 'same-origin',
            body: formData
        })
        .then((response) =>
            if not response.ok
                throw new Error(
                    utils.format("error: {status} {message}", {
                        status: response.status,
                        message: response.statusText}))

            return response.json()  # Promise
        )
        .then((data) =>
            if data.url_delete
                @addLike(data)
            else if data.url_create
                @removeLike(data)
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

        e.preventDefault()
        e.stopPropagation()
        return

    addLike: (data) =>
        @el.href = data.url_delete
        @el.dataset.count = String(parseInt(@el.dataset.count, 10) + 1)
        @el.innerHTML = utils.format(@options.removeLikeText, {count: @el.dataset.count})

    removeLike: (data) =>
        @el.href = data.url_create
        @el.dataset.count = String(parseInt(@el.dataset.count, 10) - 1)
        @el.innerHTML = utils.format(@options.likeText, {count: @el.dataset.count})

    apiError: =>
        @el.text("api error")


stModules.like = (elms, options) ->
    return Array.from(elms).map((elm) -> new Like(elm, options))

stModules.Like = Like
