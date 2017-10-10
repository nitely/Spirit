###
    Place the flash message box fixed at the
    top of the window when the url contains a hash
###

utils = stModules.utils


hasHash = ->
    hash = window.location.hash.split("#")[1]
    return hash? and hash.length > 0


class Messages

    constructor: (el) ->
        @el = el
        @setUp()

    setUp: ->
        @placeMessages()
        @showAllCloseButtons()

        Array.from(@el.querySelectorAll('.js-messages-close-button')).forEach((elm) =>
            elm.addEventListener('click', @hideMessage)
        )

    placeMessages: =>
        if not hasHash()
            return

        @el.classList.add('is-fixed')

    showAllCloseButtons: =>
        if not hasHash()
            return

        Array.from(@el.querySelectorAll('.js-messages-close')).forEach((elm) ->
            elm.style.display = 'block'
        )

    hideMessage: (e) =>
        e.preventDefault()
        e.stopPropagation()

        e.currentTarget.closest('.js-messages-set').style.display = 'none'

        # Hide container when it's empty
        if not @hasVisibleMessages()
            @el.style.display = 'none'
            @el.classList.remove('is-fixed')

        return

    hasVisibleMessages: =>
        return not utils.isHidden(@el.querySelectorAll('.js-messages-set'))


stModules.messages = (elms) ->
    return Array.from(elms).map((elm) -> new Messages(elm))

stModules.Messages = Messages
