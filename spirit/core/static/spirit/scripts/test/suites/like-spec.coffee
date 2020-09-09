describe "like plugin tests", ->
    likeElms = null
    likes = null
    post = null
    responseData = null

    beforeEach ->
        document.body.innerHTML = """
        <div>
          <ul>
            <li><a class="js-like" href="/foo/create/" data-count="0"><i class="fa fa-heart"></i> like</a></li>
          </ul>
        </div>
        <div>
          <ul>
            <li><a class="js-like" href="foo/delete/" data-count="1"><i class="fa fa-heart"></i> remove like</a></li>
          </ul>
        </div>
        """

        responseData = {url_create: '/create/foo'}

        post = spyOn(global, 'fetch')
        post.and.callFake( -> {
            then: (func) ->
                data = func({ok: true, json: -> responseData})
                return {
                    then: (func) ->
                        func(data)
                        return {catch: -> {then: (func) -> func()}}
                }
        })

        likeElms = document.querySelectorAll('.js-like')
        likes = stModules.like(likeElms, {
            csrfToken: "foobar",
            likeText: "foo like ({count})",
            removeLikeText: "foo remove like ({count})"
        })

    it "can create the like", ->
        post.calls.reset()
        likeElms[0].click()
        expect(post.calls.any()).toEqual(true)
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/')
        expect(post.calls.argsFor(0)[1].body.get('csrfmiddlewaretoken')).toEqual("foobar")

    it "can create and remove the like", ->
        # create
        post.calls.reset()
        responseData = {url_delete: "/foo/delete/"}
        likeElms[0].click()
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/')
        expect(likeElms[0].textContent).toEqual("foo remove like (1)")

        # remove
        post.calls.reset()
        responseData = {url_create: "/foo/create/"}
        likeElms[0].click()
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/delete/')
        expect(likeElms[0].textContent).toEqual("foo like (0)")

        # create again... and so on...
        post.calls.reset()
        responseData = {url_delete: "/foo/delete/"}
        likeElms[0].click()
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/')
        expect(likeElms[0].textContent).toEqual("foo remove like (1)")

    it "will tell about an api change", ->
        responseData = {unknown: null}
        likeElms[0].click()
        expect(likeElms[0].textContent).toEqual("api error")

    it "prevents from multiple posts while sending", ->
        post.and.callFake( -> {then: -> {then: -> {catch: -> {then: -> }}}})
        likeElms[0].click()

        # next click should do nothing
        post.calls.reset()
        likeElms[0].click()
        expect(post.calls.any()).toEqual(false)

    it "prevents the default click behaviour", ->
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("click", false, true)

        stopPropagation = spyOn(evt, 'stopPropagation')
        preventDefault = spyOn(evt, 'preventDefault')

        likeElms[0].dispatchEvent(evt)
        expect(stopPropagation).toHaveBeenCalled()
        expect(preventDefault).toHaveBeenCalled()
