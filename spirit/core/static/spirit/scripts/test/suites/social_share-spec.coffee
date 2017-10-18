describe "social-share plugin tests", ->
    social_share = null

    isHidden = stModules.utils.isHidden

    beforeEach ->
        fixtures = jasmine.getFixtures()
        fixtures.fixturesPath = 'base/test/fixtures/'
        loadFixtures('social_share.html')

        social_share = document.querySelectorAll('.js-share')
        stModules.socialShare(social_share)

    it "shows the share dialog", ->
        expect(isHidden([document.querySelector('.test-1')])).toEqual(true)
        social_share[0].click()
        expect(isHidden([document.querySelector('.test-1')])).toEqual(false)
        expect(isHidden([document.querySelector('.test-2')])).toEqual(true)

        social_share[1].click()
        expect(isHidden([document.querySelector('.test-1')])).toEqual(true)
        expect(isHidden([document.querySelector('.test-2')])).toEqual(false)

    it "prevents the default click behaviour on share click", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        social_share[0].dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()

    it "closes the dialog", ->
        social_share[0].click()
        expect(isHidden([document.querySelector('.test-1')])).toEqual(false)

        document.querySelector('.test-1').querySelector('.share-close').click()
        expect(isHidden([document.querySelector('.test-1')])).toEqual(true)

    it "prevents the default click behaviour on close dialog", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        document.querySelector('.test-1').querySelector('.share-close').dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()

    it "auto selects the share link on focus", ->
        social_share[0].click()
        shareInput = document.querySelector('.test-1').querySelector('.share-url')
        shareInput.focus()

        #selection = $shareInput.val().substring $shareInput[0].selectionStart, $shareInput[0].selectionEnd

        #expect(selection).toEqual "link"
        #TODO: test, override SocialShare.select

    it "prevents the default behaviour on input mouseup", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("mouseup", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        document.querySelector('.test-1').querySelector('.share-url').dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()
