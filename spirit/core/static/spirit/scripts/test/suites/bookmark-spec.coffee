describe "bookmark plugin tests", ->
    comments = null
    bookmarks = null
    mark = null
    Bookmark = null
    Mark = null
    post = null

    beforeEach ->
        document.body.innerHTML = """
            <div class="comment" data-number="1"></div>
            <div class="comment" data-number="2"></div>
        """

        # Promise is async, so must callFake a sync thing
        post = spyOn(global, 'fetch')
        post.and.callFake( -> {
            then: (func) ->
                func({ok: true})
                return {
                    catch: -> {then: (func) -> func()}
                }
        })

        comments = document.querySelectorAll('.comment')
        bookmarks = stModules.bookmark(comments, {
            csrfToken: "foobar",
            target: "/foo/"
        })
        mark = bookmarks[0].mark
        Bookmark = stModules.Bookmark
        Mark = stModules.Mark

        # Trigger all waypoints
        bookmarks.forEach((bm) ->
            bm.onWaypoint()
        )

    it "sends the first comment number", ->
        expect(post.calls.any()).toEqual(true)
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/')
        expect(post.calls.argsFor(0)[1].body.get('csrfmiddlewaretoken')).toEqual("foobar")
        expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1')

    it "stores the last comment number", ->
        expect(mark.commentNumber).toEqual(2)

    it "stores the same mark in every comment", ->
        bookmark_1 = bookmarks[0]
        bookmark_2 = bookmarks[bookmarks.length - 1]
        expect(bookmark_1.mark).toEqual(bookmark_2.mark)

    it "does not post on scroll up", ->
        post.calls.reset()
        bookmark_1 = bookmarks[0]
        bookmark_1.onWaypoint()
        expect(mark.commentNumber).toEqual(2)
        expect(post.calls.any()).toEqual(false)

    it "does post on scroll down", ->
        post.calls.reset()
        bookmark_2 = bookmarks[bookmarks.length - 1]
        bookmark_2.number = 999
        bookmark_2.onWaypoint()
        expect(mark.commentNumber).toEqual(999)
        expect(post.calls.any()).toEqual(true)

    it "gets the comment number from the address bar", ->
        org_location_hash = window.location.hash
        window.location.hash = ""
        try
            window.location.hash = "http://example.com/foo/#c5"
            newMark = new Mark()
            # it substract 1 from the real comment number
            expect(newMark.commentNumber).toEqual 4

            window.location.hash = "http://example.com/foo/"
            newMark = new Mark()
            expect(newMark.commentNumber).toEqual 0

            window.location.hash = "http://example.com/foo/#foobar5"
            newMark = new Mark()
            expect(newMark.commentNumber).toEqual 0
        finally
            window.location.hash = org_location_hash

    it "sends only one comment number in a given time", ->
        post.calls.reset()
        expect(post.calls.any()).toEqual(false)

        # won't post if already sending
        mark.commentNumber = 0
        bookmark_2 = bookmarks[bookmarks.length - 1]
        mark.isSending = true
        bookmark_2.onWaypoint()
        expect(post.calls.any()).toEqual(false)

        mark.commentNumber = 0
        post.calls.reset()
        mark.isSending = false
        bookmark_2.onWaypoint()
        expect(post.calls.any()).toEqual(true)
        expect(mark.isSending).toEqual(false)

    it "sends current comment number after sending previous when current > previous", ->
        post.calls.reset()
        expect(post.calls.any()).toEqual(false)

        post.and.callFake( -> {
            then: (func) ->
                # isSending == true, so this should just put it in queue
                bookmark_2 = bookmarks[bookmarks.length - 1]
                bookmark_2.onWaypoint()
                func({ok: true})
                return {
                    catch: -> {then: (func) -> func()}
                }
        })

        mark.commentNumber = -1
        bookmark_1 = bookmarks[0]
        bookmark_1.onWaypoint()
        expect(post.calls.count()).toEqual(2)
        expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1')
        expect(post.calls.argsFor(1)[1].body.get('comment_number')).toEqual('2')

        # Should do nothing
        post.calls.reset()
        bookmark_1.onWaypoint()
        expect(post.calls.any()).toEqual(false)

    it "sends next after server error", ->
        post.calls.reset()
        expect(post.calls.any()).toEqual(false)

        post.and.callFake( -> {
            then: ->
                # isSending == true, so this should just put it in queue
                bookmark_2 = bookmarks[bookmarks.length - 1]
                bookmark_2.onWaypoint()
                return {
                    catch: (func) ->
                      func({message: 'connection error'})
                      return {then: (func) -> func()}
                }
        })

        log = spyOn(console, 'log')
        log.and.callFake( -> )

        mark.commentNumber = -1
        bookmark_1 = bookmarks[0]
        bookmark_1.onWaypoint()
        expect(post.calls.count()).toEqual(2)
        expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1')
        expect(post.calls.argsFor(1)[1].body.get('comment_number')).toEqual('2')

        expect(log.calls.count()).toEqual(2)
        expect(log.calls.argsFor(0)[0]).toEqual('connection error')
        expect(log.calls.argsFor(1)[0]).toEqual('connection error')
