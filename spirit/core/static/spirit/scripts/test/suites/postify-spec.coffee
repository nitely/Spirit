describe "postify plugin tests", ->
    a_post = null
    plugin_postify = null

    isHidden = stModules.utils.isHidden

    beforeEach ->
        document.body.innerHTML = """
        <a class="js-post" href="/link1/">link</a>
        <a class="js-post" href="/link2/">link 2</a>
        """

        a_post = document.querySelectorAll('.js-post')
        plugin_postify = stModules.postify(a_post, {
            csrfToken: "foobar"
        })

    afterEach ->
        Array.from(document.querySelectorAll('.js-postify-form')).forEach((elm) ->
            elm.parentNode.removeChild(elm)
        )

    it "prevents the default click behaviour on click", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)
        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        submit = spyOn(window.HTMLFormElement.prototype, 'submit')
        submit.and.callFake( -> )

        a_post[0].dispatchEvent(evt)
        expect(submit.calls.count()).toEqual(1)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()

    it "submits the form", ->
        submit = spyOn(window.HTMLFormElement.prototype, 'submit')
        submit.and.callFake( -> )

        a_post[0].click()
        form = document.querySelector('.js-postify-form')

        expect(submit.calls.count()).toEqual(1)
        expect(form.getAttribute('action')).toEqual("/link1/")
        expect(isHidden([form])).toEqual(true)
        expect(document.querySelector('input[name=csrfmiddlewaretoken]').value).toEqual("foobar")
