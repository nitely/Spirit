describe "move_comments plugin tests", ->
    show_move_comments = null
    plugin_move_comments = null

    isHidden = stModules.utils.isHidden

    beforeEach ->
        document.body.innerHTML = """
        <a class="js-show-move-comments" href="#" >Select comments to move</a>
        <div class="js-move-comments-form" style="display:none;">
          <div class="move-container">
            <label>Topic id:</label>
            <input id="id_move_comments_topic" type="text" value="10" />
            <a class="js-move-comments-button" href="#move_url">Move</a>
          </div>
        </div>
        <div class="js-comment" data-pk="1">
          <ul class="js-move-comment-checkbox-list"></ul>
        </div>
        <div class="js-comment" data-pk="2">
          <ul class="js-move-comment-checkbox-list"></ul>
        </div>
        """

        show_move_comments = document.querySelectorAll('.js-show-move-comments')
        plugin_move_comments = stModules.moveComments(show_move_comments, {
            csrfToken: "foobar",
            target: "/foo/"
        })

    afterEach ->
        # Fixture will only remove itself not nodes appended to body
        # so we have to manually remove forms
        Array.from(document.querySelectorAll('.js-move-comment-form')).forEach((elm) ->
            elm.parentNode.removeChild(elm)
        )

    it "shows the move form on click", ->
        expect(isHidden(document.querySelectorAll(".js-move-comments-form"))).toEqual(true)
        expect(document.querySelectorAll(".js-move-comment-checkbox").length).toEqual(0)

        show_move_comments[0].click()
        expect(isHidden(document.querySelectorAll(".js-move-comments-form"))).toEqual(false)
        expect(document.querySelectorAll(".js-move-comment-checkbox").length).toEqual(2)

    it "prevents the default click behaviour on show move comments", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)
        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        show_move_comments[0].dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()

    it "prevents the default click behaviour on submit", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)
        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        submit = spyOn(window.HTMLFormElement.prototype, 'submit')
        submit.and.callFake( -> )

        document.querySelector(".js-move-comments-button").dispatchEvent(evt)
        expect(submit.calls.count()).toEqual(1)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()

    it "submits the form", ->
        submit = spyOn(window.HTMLFormElement.prototype, 'submit')
        submit.and.callFake( -> )

        document.querySelector(".js-show-move-comments").click()
        document.querySelector(".js-move-comments-button").click()
        form = document.querySelector(".js-move-comment-form")

        expect(submit.calls.count()).toEqual(1)
        expect(form.getAttribute('action')).toEqual("/foo/")
        expect(isHidden([form])).toEqual(true)
        expect(form.querySelector("input[name=csrfmiddlewaretoken]").value).toEqual("foobar")
        expect(form.querySelector("input[name=topic]").value).toEqual("10")
        expect(form.querySelectorAll("input[name=comments]").length).toEqual(2)
