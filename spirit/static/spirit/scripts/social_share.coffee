###
  Social share popup
###

$ = jQuery


class SocialShare

  constructor: (el) ->
    @el = $(el)
    @dialog = $(@el.data "dialog")
    do @setUp

  setUp: ->
    @el.on 'click', @showDialog
    @el.on 'click', @stopClick

    $shareClose = @dialog.find '.share-close'
    $shareClose.on 'click', @closeDialog
    $shareClose.on 'click', @stopClick

    # Auto selection
    $shareInput = @dialog.find '.share-url'
    $shareInput.on 'focus', @select
    $shareInput.on 'mouseup', @stopClick  # Fix for chrome and safari

  showDialog: =>
    do $('.share').hide
    do @dialog.show
    return

  closeDialog: =>
    do @dialog.hide
    return

  select: ->
    do $(@).select
    return

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.fn.extend
  social_share: ->
    @each ->
      if not $(@).data 'plugin_social_share'
        $(@).data 'plugin_social_share', new SocialShare(@)

$.fn.social_share.SocialShare = SocialShare