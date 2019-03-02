(function() {
  describe("comment_diff plugin tests", function() {
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      return loadFixtures('comment_diff.html');
    });
    return it("diffes comments", function() {
      var comments;
      comments = document.querySelectorAll('.comment');
      stModules.commentDiff(comments);
      expect(comments[0].innerHTML).toEqual('Hello');
      expect(comments[1].innerHTML).toEqual('Hello<ins class="diff"> world</ins>');
      return expect(comments[2].innerHTML).toEqual('Hello world<ins class="diff">!</ins>');
    });
  });

}).call(this);

//# sourceMappingURL=comment_diff-spec.js.map
