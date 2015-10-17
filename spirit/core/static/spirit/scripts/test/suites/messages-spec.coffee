describe "messages plugin tests", ->
    Messages = null

    beforeEach ->
        fixtures = jasmine.getFixtures()
        fixtures.fixturesPath = 'base/test/fixtures/'
        loadFixtures('messages.html')

        # messages = $('.js-messages').messages()
        Messages = $.fn.messages.Messages

    it "doesnt break selector chaining", ->
        messages = $('.js-messages-dummy').messages()
        expect(messages).toEqual($('.js-messages-dummy'))
        expect(messages.length).toEqual(2)

    it "does nothing when no hash", ->
        messages = $('.js-messages').messages()
        expect(messages.hasClass('is-fixed')).toEqual(false)
        expect($('.js-messages-close').is(":hidden")).toEqual(true)

    it "places the messages when there is a hash", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            messages = $('.js-messages').messages()
            expect(messages.hasClass('is-fixed')).toEqual(true)
        finally
            window.location.hash = org_location_hash

    it "shows all the close buttons", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            messages = $('.js-messages').messages()
            expect($('.js-messages-close').is(":hidden")).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "closes/hides the message", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            messages = $('.js-messages').messages()
            first_set = messages.find('.js-messages-set').first()
            first_set.find('.js-messages-close-button').trigger('click')
            expect(first_set.is(":hidden")).toEqual(true)
            expect(messages.is(":hidden")).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "closes/hides the container when no more visible messages", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            messages = $('.js-messages').messages()
            messages.find('.js-messages-close-button').trigger('click')
            expect(messages.is(":hidden")).toEqual(true)
            expect(messages.hasClass('is-fixed')).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "prevents the default click behaviour on close message", ->
        event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
        stopPropagation = spyOn event, 'stopPropagation'
        preventDefault = spyOn event, 'preventDefault'

        messages = $('.js-messages').messages()
        messages.find('.js-messages-close-button').first().trigger(event)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()
