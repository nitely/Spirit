###
  Place the flash message box fixed at the
  top of the window when the url contains a hash
###

$ = jQuery


class Messages

  constructor: (el) ->
    @el = $(el)
    @allCloseButtons = @el.find('.js-message-close')
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

    @allCloseButtons.show()

  hideMessage: (e) =>
    $(e.currentTarget)
      .closest('.js-message')
      .hide()

    $messageSet = $(e.currentTarget).closest('.js-messages-set')

    if not @hasVisibleMessages($messageSet)
      $messageSet.hide()

    if not @hasVisibleMessages(@el)
      @el.hide()

    return

  hasVisibleMessages: (el) =>
    visibleMessages = (e for e in el.find('.js-message') when e.is(":visible"))
    return visibleMessages.length > 0

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return

  hasHash: ->
    hash = window.location.hash.split("#")[1]
    return hash? and hash.length > 0


$.fn.extend
  messages: ->
    @each ->
      if not $(@).data('plugin_messages')
        $(@).data('plugin_messages', new Messages(@))

$.fn.messages.Messages = Messages
