describe "tab plugin tests", ->
    tabElms = null
    tabs = null
    Tab = null

    beforeEach ->
        document.body.innerHTML = """
        <div class="js-tabs-container">
          <ul>
            <li><a class="js-tab" href="#" data-related=".js-search-content">t1</a></li>
            <li><a class="js-tab" href="#" data-related=".js-notifications-content">t2</a></li>
            <li><a class="js-tab" href="#" data-related=".js-user-content">t3</a></li>
          </ul>
          <div class="js-tab-content js-user-content" style="display:none;"></div>
          <div class="js-tab-content js-notifications-content" style="display:none;"></div>
          <div class="js-tab-content js-search-content" style="display:none;"></div>
        </div>
        """

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
        expect(tab_content_first.style.display).toEqual('')

        tab_content_last = document.querySelector(
          tabElms[tabElms.length - 1].dataset.related)
        expect(tab_content_last.style.display).toEqual('none')

        tabElms[tabElms.length - 1].click()
        expect(tab_content_last.style.display).toEqual('')
        expect(tab_content_first.style.display).toEqual('none')

    it "hides the clicked tab content if is selected", ->
        tab_content_first = document.querySelector(tabElms[0].dataset.related)
        expect(tab_content_first.style.display).toEqual('none')

        tabElms[0].click()
        expect(tab_content_first.style.display).toEqual('')

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
