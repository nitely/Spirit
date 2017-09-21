(function() {
  describe("editor plugin tests", function() {
    return it("returns the emoji list", function() {
      var emojis;
      emojis = $.emoji_list();
      return expect(emojis[0]).toEqual({
        "name": "+1"
      });
    });
  });

}).call(this);

//# sourceMappingURL=emoji_list-spec.js.map
