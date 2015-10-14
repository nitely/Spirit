###
  Generic tabs
###

$ = jQuery


class Tab

  constructor: (el) ->
    @el = $(el)
    do @setUp

  setUp: ->
    @el.on 'click', @tabSwitch
    @el.on 'click', @stopClick

  tabSwitch: =>
    do @hideAllTabsContent

    if @el.hasClass "is-selected"
      @el.removeClass "is-selected"
    else
      do @unselectAllTabs
      do @selectTab
      do @showTabContent

    return

  hideAllTabsContent: =>
    $tabs_container = @el.closest ".js-tabs-container"
    $tabs_content = $tabs_container.find ".js-tab-content"
    do $tabs_content.hide

  unselectAllTabs: =>
    $tabs_container = @el.closest ".js-tabs-container"
    $tabs = $tabs_container.find ".js-tab"
    $tabs.removeClass "is-selected"

  selectTab: =>
    @el.addClass "is-selected"

  showTabContent: =>
    tab_content = @el.data "related"
    do $(tab_content).show

  stopClick: (e) ->
    do e.preventDefault
    do e.stopPropagation
    return


$.extend
  tab: ->
    $('.js-tab').each ->
      if not $(@).data 'plugin_tab'
        $(@).data 'plugin_tab', new Tab(@)

$.tab.Tab = Tab