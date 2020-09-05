###
    Move comments to other topic
###


class MoveCommentBox

    defaults: {
        csrfToken: "csrf_token",
        target: "#post_url"
    }

    constructor: (options) ->
        @el = document.querySelector('.js-move-comments-form')
        @options = Object.assign({}, @defaults, options)
        @setUp()

    setUp: ->
        @el
            .querySelector('.js-move-comments-button')
            .addEventListener('click', @moveComments)

    moveComments: (e) =>
        e.preventDefault()
        e.stopPropagation()

        formElm = document.createElement('form')
        formElm.className = 'js-move-comment-form'
        formElm.action = @options.target
        formElm.method = 'POST'
        formElm.style.display = 'none'
        document.body.appendChild(formElm)

        inputCSRFElm = document.createElement('input')
        inputCSRFElm.name = 'csrfmiddlewaretoken'
        inputCSRFElm.type = 'hidden'
        inputCSRFElm.value = @options.csrfToken
        formElm.appendChild(inputCSRFElm)

        inputTopicIdElm = document.createElement('input')
        inputTopicIdElm.name = 'topic'
        inputTopicIdElm.type = 'text'
        inputTopicIdElm.value = @el.querySelector('#id_move_comments_topic').value
        formElm.appendChild(inputTopicIdElm)

        # Append all selection inputs
        Array.from(document.querySelectorAll('.js-move-comment-checkbox')).forEach((elm) ->
            formElm.appendChild(elm.cloneNode(false))
        )

        formElm.submit()
        return

    isHidden: =>
        return @el.style.display == 'none'

    show: =>
        @el.style.display = 'block'
        return


class MoveComment
    #TODO: prefix classes with js-

    constructor: (el, box) ->
        @el = el
        @box = box
        @setUp()

    setUp: ->
        @el.addEventListener('click', @showMoveComments)

    showMoveComments: (e) =>
        e.preventDefault()
        e.stopPropagation()

        if @box.isHidden()
            @box.show()
            @addCommentSelection()

        return

    addCommentSelection: =>
        Array.from(document.querySelectorAll('.js-move-comment-checkbox-list')).forEach((elm) ->
            liElm = document.createElement('li')
            elm.appendChild(liElm)

            inputCheckboxElm = document.createElement('input')
            inputCheckboxElm.className = 'js-move-comment-checkbox'
            inputCheckboxElm.name = 'comments'
            inputCheckboxElm.type = 'checkbox'
            inputCheckboxElm.value = elm.closest('.js-comment').dataset.pk
            liElm.appendChild(inputCheckboxElm)

            return
        )


stModules.moveComments = (elms, options) ->
    box = new MoveCommentBox(options)
    return Array.from(elms).map((elm) -> new MoveComment(elm, box))

stModules.MoveCommentBox = MoveCommentBox
stModules.MoveComment = MoveComment
