describe "comment_diff plugin tests", ->

    beforeEach ->
        fixtures = jasmine.getFixtures()
        fixtures.fixturesPath = 'base/test/fixtures/'
        loadFixtures('comment_diff.html')

    it "diffes comments", ->
        comments = document.querySelectorAll('.comment')
        stModules.commentDiff(comments)
        expect(comments[0].innerHTML).toEqual('Hello')
        expect(comments[1].innerHTML).toEqual('Hello<ins> world</ins>')
        expect(comments[2].innerHTML).toEqual('Hello world<ins>!</ins>')
