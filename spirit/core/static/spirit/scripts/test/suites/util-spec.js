(function() {
  describe("util format tests", function() {
    return it("formats a string", function() {
      var result;
      result = stModules.utils.format("{foo} foobar {bar} {bad}", {
        foo: "foo text",
        bar: "bar text"
      });
      return expect(result).toEqual("foo text foobar bar text {bad}");
    });
  });

}).call(this);

//# sourceMappingURL=util-spec.js.map
