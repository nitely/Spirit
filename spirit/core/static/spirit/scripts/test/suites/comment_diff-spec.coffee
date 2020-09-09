describe "comment_diff plugin tests", ->

    beforeEach ->
        document.body.innerHTML = """
        <div class="comment">Hello</div>
        <div class="comment">Hello world</div>
        <div class="comment">Hello world!</div>
        """

    it "diffes comments", ->
        comments = document.querySelectorAll('.comment')
        stModules.commentDiff(comments)
        expect(comments[0].innerHTML).toEqual('Hello')
        expect(comments[1].innerHTML).toEqual('Hello<ins class="diff"> world</ins>')
        expect(comments[2].innerHTML).toEqual('Hello world<ins class="diff">!</ins>')
