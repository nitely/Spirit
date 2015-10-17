###
    Social share popup
###

$ = jQuery


class SocialShare

    constructor: (el) ->
        @el = $(el)
        @dialog = $(@el.data("dialog"))
        @setUp()

    setUp: ->
        @el.on('click', @showDialog)
        @el.on('click', @stopClick)

        $shareClose = @dialog.find('.share-close')
        $shareClose.on('click', @closeDialog)
        $shareClose.on('click', @stopClick)

        # Auto selection
        $shareInput = @dialog.find('.share-url')
        $shareInput.on('focus', @select)
        $shareInput.on('mouseup', @stopClick)  # Fix for chrome and safari

    showDialog: =>
        $('.share').hide()
        @dialog.show()
        return

    closeDialog: =>
        @dialog.hide()
        return

    select: ->
        $(@).select()
        return

    stopClick: (e) ->
        e.preventDefault()
        e.stopPropagation()
        return


$.fn.extend
    social_share: ->
        @each( ->
            if not $(@).data('plugin_social_share')
                $(@).data('plugin_social_share', new SocialShare(@))
        )

$.fn.social_share.SocialShare = SocialShare
