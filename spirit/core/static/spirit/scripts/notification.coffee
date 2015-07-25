###
  Notifications ajax tab
  requires: util.js, tab.js
###

$ = jQuery


class Notification

  defaults:
    notificationUrl: "#ajax",
    notificationListUrl: "#show-all",
    mentionTxt: "{user} mention you on {topic}",
    commentTxt: "{user} has commented on {topic}",
    showAll: "Show all",
    empty: "Nothing to show",
    unread: "unread"

  constructor: (el, options) ->
    @el = $(el)
    @options = $.extend {}, @defaults, options
    @tabNotificationContent = $(@el.data "related")
    do @setUp

  setUp: ->
    # on first click
    @el.one 'click', @tabSwitch
    @el.one 'click', @stopClick

  tabSwitch: =>
    get = $.getJSON @options.notificationUrl

    get.done (data, status, jqXHR) =>
      if data.n.length > 0
        @addNotifications data
      else
        do @addIsEmptyTxt

    get.fail (jqxhr, textStatus, error) =>
      @addErrorTxt textStatus, error

    get.always =>
      do @ajaxDone

    return

  addNotifications: (data) =>
    unread = "<span class=\"row-unread\">#{ @options.unread }</span>"

    $.each data.n, (i, obj) =>
      if obj.action is 1
        txt = @options.mentionTxt
      else
        txt = @options.commentTxt

      if not obj.is_read
        txt = "#{ txt } #{ unread }"

      link = "<a href=\"#{ obj.url }\">#{ obj.title }</a>"
      txt = $.format txt, {user: obj.user, topic: link}
      @tabNotificationContent.append "<div>#{ txt }</div>"

    showAllLink = "<a href=\"#{ @options.notificationListUrl }\">#{ @options.showAll }</a>"
    @tabNotificationContent.append "<div>#{ showAllLink }</div>"

  addIsEmptyTxt: =>
    @tabNotificationContent.append "<div>#{ @options.empty }</div>"

  addErrorTxt: (textStatus, error) =>
    @tabNotificationContent.append "<div>Error: #{ textStatus }, #{ error }</div>"

  ajaxDone: =>
    @el.addClass "js-tab"
    do $.tab
    @el.trigger 'click'

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.extend
  notification: (options) ->
    $('.js-tab-notification').each ->
      if not $(@).data 'plugin_notification'
        $(@).data 'plugin_notification', new Notification(@, options)

$.notification.Notification = Notification