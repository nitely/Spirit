describe "tab plugin tests", ->
    tabElms = null
    tabs = null
    Tab = null

    beforeEach ->
        fixtures = do jasmine.getFixtures
        fixtures.fixturesPath = 'base/test/fixtures/'
        loadFixtures 'tab.html'

        tabElms = document.querySelectorAll('.js-tab')
        tabs = stModules.tab(tabElms)
        Tab = stModules.Tab

    it "selects the clicked tab", ->
        tabElms[0].click()
        expect(tabElms[0].classList.contains('is-selected')).toEqual true

        tabElms[tabElms.length - 1].click()
        expect(tabElms[tabElms.length - 1].classList.contains('is-selected')).toEqual true
        expect(tabElms[0].classList.contains('is-selected')).toEqual false

    it "unselects the clicked tab if is selected", ->
        tabElms[0].click()
        expect(tabElms[0].classList.contains('is-selected')).toEqual true

        tabElms[0].click()
        expect(tabElms[0].classList.contains('is-selected')).toEqual false

    it "shows the clicked tab content", ->
        tab_content_first = document.querySelector(tabElms[0].dataset.related)
        expect(tab_content_first.style.display).toEqual('none')

        tabElms[0].click()
        expect(tab_content_first.style.display).toEqual('block')

        tab_content_last = document.querySelector(
          tabElms[tabElms.length - 1].dataset.related)
        expect(tab_content_last.style.display).toEqual('none')

        tabElms[tabElms.length - 1].click()
        expect(tab_content_last.style.display).toEqual('block')
        expect(tab_content_first.style.display).toEqual('none')

    it "hides the clicked tab content if is selected", ->
        tab_content_first = document.querySelector(tabElms[0].dataset.related)
        expect(tab_content_first.style.display).toEqual('none')

        tabElms[0].click()
        expect(tab_content_first.style.display).toEqual('block')

        tabElms[0].click()
        expect(tab_content_first.style.display).toEqual('none')

    it "prevents the default click behaviour", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        tabElms[0].dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()
