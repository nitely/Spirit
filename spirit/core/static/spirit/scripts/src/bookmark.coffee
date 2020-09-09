###
    A library to tell the server how far you have scrolled down.
    requires: modules, waypoints
###

Waypoint = if Waypoint? then Waypoint else window.Waypoint


class Mark
    ## This is shared among a set of bookmarks

    defaults: {
        csrfToken: "csrf_token",
        target: "target url"
    }

    constructor: (options) ->
        @options = Object.assign({}, @defaults, options)
        @isSending = false
        @commentNumber = @_getCommentNumber()
        @numberQueued = @commentNumber

    _getCommentNumber: ->
        commentNumber = window.location.hash.split("#c")[1]
        commentNumber = parseInt(commentNumber, 10)  # base 10

        if isNaN(commentNumber)
            commentNumber = 0
        else
            # workaround to always send comment number from hash
            commentNumber -= 1

        return commentNumber

    canSend: (number) =>
        Number.isInteger(number) or console.error('not a number')
        return number > @commentNumber

    sendMark: (number) =>
        if not @canSend(number)
            return

        @numberQueued = number

        if @isSending
            return

        @isSending = true
        @commentNumber = number

        form = new FormData()
        form.append('csrfmiddlewaretoken', @options.csrfToken)
        form.append('comment_number', String(number))

        headers = new Headers()
        headers.append("X-Requested-With", "XMLHttpRequest")

        fetch(@options.target, {
            method: "POST",
            headers: headers,
            credentials: 'same-origin',
            body: form
        })
        .then((response) =>
            response.ok or console.log({
                status: response.status,
                statusText: response.statusText
            })
        )
        .catch((error) =>
            console.log(error.message)
        )
        .then( =>
            @isSending = false
            @sendMark(@numberQueued)
        )


class Bookmark

    constructor: (el, mark) ->
        @el = el
        @mark = mark
        @number = @_getNumber()
        @waypoint = @_addWaypointListener(el, @onWaypoint)

    _addWaypointListener: (elm, handler) ->
        return new Waypoint({
            element: elm,
            handler: handler,
            offset: '100%'
        })

    _getNumber: =>
        number = parseInt(@el.dataset.number, 10)
        not isNaN(number) or console.error('comment number is NaN')
        return number

    onWaypoint: =>
        @mark.sendMark(@number)
        return


stModules.bookmark = (elms, options) ->
    mark = new Mark(options)

    return Array.from(elms).map((elm) ->
        return new Bookmark(elm, mark)
    )

stModules.Bookmark = Bookmark
stModules.Mark = Mark
