describe "messages plugin tests", ->

    isHidden = stModules.utils.isHidden

    beforeEach ->
        document.body.innerHTML = """
        <div class="js-messages">
          <div class="js-messages-set">
            <ul>
              <li>success 1</li>
              <li>success 2</li>
            </ul>
            <div class="js-messages-close" style="display: none">
              <i class="js-messages-close-button"></i>
            </div>
          </div>
          <div class="js-messages-set">
            <ul>
              <li>error 1</li>
              <li>error 2</li>
            </ul>
            <div class="js-messages-close" style="display: none">
              <i class="js-messages-close-button"></i>
            </div>
          </div>
        </div>
        <div class="js-messages-dummy"></div>
        <div class="js-messages-dummy"></div>
        """

    it "attaches all messages", ->
        messages = stModules.messages(document.querySelectorAll('.js-messages-dummy'))
        expect(messages.length).toEqual(2)

    it "does nothing when no hash", ->
        message = document.querySelector('.js-messages-dummy')
        stModules.messages([message])
        expect(message.classList.contains('is-fixed')).toEqual(false)
        expect(isHidden(document.querySelectorAll('.js-messages-close'))).toEqual(true)

    it "places the messages when there is a hash", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            message = document.querySelector('.js-messages')
            stModules.messages([message])
            expect(message.classList.contains('is-fixed')).toEqual(true)
        finally
            window.location.hash = org_location_hash

    it "shows all the close buttons", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            stModules.messages(document.querySelectorAll('.js-messages'))
            expect(isHidden(document.querySelectorAll('.js-messages-close'))).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "closes/hides the message", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            messages = document.querySelectorAll('.js-messages')
            stModules.messages(messages)
            first_set = document.querySelector('.js-messages').querySelector('.js-messages-set')
            first_set.querySelector('.js-messages-close-button').click()
            expect(isHidden([first_set])).toEqual(true)
            expect(isHidden(messages)).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "closes/hides the container when no more visible messages", ->
        org_location_hash = window.location.hash
        try
            window.location.hash = "#p1"
            message = document.querySelector('.js-messages')
            stModules.messages([message])
            Array.from(message.querySelectorAll('.js-messages-close-button')).forEach((elm) ->
                elm.click()
            )
            expect(isHidden([message])).toEqual(true)
            expect(message.classList.contains('is-fixed')).toEqual(false)
        finally
            window.location.hash = org_location_hash

    it "prevents the default click behaviour on close message", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        message = document.querySelector('.js-messages')
        stModules.messages([message])
        message.querySelector('.js-messages-close-button').dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()
