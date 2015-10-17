###
    Generic tabs
###

$ = jQuery


class Tab

    constructor: (el) ->
        @el = $(el)
        @setUp()

    setUp: ->
        @el.on('click', @tabSwitch)
        @el.on('click', @stopClick)

    tabSwitch: =>
        @hideAllTabsContent()

        if @el.hasClass("is-selected")
            @el.removeClass("is-selected")
        else
            @unselectAllTabs()
            @selectTab()
            @showTabContent()

        return

    hideAllTabsContent: =>
        $tabs_container = @el.closest(".js-tabs-container")
        $tabs_content = $tabs_container.find(".js-tab-content")
        $tabs_content.hide()

    unselectAllTabs: =>
        $tabs_container = @el.closest(".js-tabs-container")
        $tabs = $tabs_container.find(".js-tab")
        $tabs.removeClass("is-selected")

    selectTab: =>
        @el.addClass("is-selected")

    showTabContent: =>
        tab_content = @el.data("related")
        $(tab_content).show()

    stopClick: (e) ->
        e.preventDefault()
        e.stopPropagation()
        return


$.extend
    tab: ->
        $('.js-tab').each( ->
            if not $(@).data('plugin_tab')
                $(@).data('plugin_tab', new Tab(@))
        )

$.tab.Tab = Tab
