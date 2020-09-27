###
    Generic tabs
###


class Tab

    constructor: (el) ->
        @el = el
        @containerElm = @el.closest(".js-tabs-container")
        @setUp()

    setUp: ->
        @el.addEventListener('click', @tabSwitch)

    tabSwitch: (e) =>
        e.preventDefault()
        e.stopPropagation()
        @hideAllTabsContent()

        if @el.classList.contains('is-selected')
            @el.classList.remove('is-selected')
        else
            @unselectAllTabs()
            @selectTab()
            @showTabContent()

        return

    hideAllTabsContent: =>
        tabContentElms = @containerElm.querySelectorAll(".js-tab-content")
        Array.from(tabContentElms).forEach((elm) ->
            elm.style.display = 'none'
        )

    unselectAllTabs: =>
        tabElms = @containerElm.querySelectorAll(".js-tab")
        Array.from(tabElms).forEach((elm) ->
            elm.classList.remove('is-selected')
        )

    selectTab: =>
        @el.classList.add('is-selected')

    showTabContent: =>
        @containerElm
            .querySelector(@el.dataset.related)
            .style
            .removeProperty('display')
        @containerElm
            .querySelector(@el.dataset.related)
            .querySelector('input')?.focus()


stModules.tab = (elms) -> Array.from(elms).map((elm) -> new Tab(elm))
stModules.Tab = Tab
