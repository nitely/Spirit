###
    Place the flash message box fixed at the
    top of the window when the url contains a hash
###

$ = jQuery


class Messages

    constructor: (el) ->
        @el = $(el)
        @allCloseButtons = @el.find('.js-messages-close-button')
        @setUp()

    setUp: ->
        @placeMessages()
        @showAllCloseButtons()
        @allCloseButtons.on('click', @hideMessage)
        @allCloseButtons.on('click', @stopClick)

    placeMessages: =>
        if not @hasHash()
            return

        @el.addClass('is-fixed')

    showAllCloseButtons: =>
        if not @hasHash()
            return

        @el
            .find('.js-messages-close')
            .show()

    hideMessage: (e) =>
        $(e.currentTarget)
            .closest('.js-messages-set')
            .hide()

        if not @hasVisibleMessages()
            @el.hide()
            @el.removeClass('is-fixed')

        return

    hasVisibleMessages: () =>
        return @el
            .find('.js-messages-set')
            .is(":visible")

    stopClick: (e) ->
        e.preventDefault()
        e.stopPropagation()
        return

    hasHash: ->
        hash = window.location.hash.split("#")[1]
        return hash? and hash.length > 0


$.fn.extend
    messages: ->
        @each( ->
            if not $(@).data('plugin_messages')
                $(@).data('plugin_messages', new Messages(@))
        )

$.fn.messages.Messages = Messages
