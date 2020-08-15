(function() {
  describe("editor image upload plugin tests", function() {
    return it("has correct meta data", function() {
      var editor, fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('editor.html');
      editor = stModules.editorImageUpload(document.querySelectorAll('.js-reply'))[0];
      return expect(editor.meta).toEqual({
        fieldName: "image",
        tag: "![{text}]({url})",
        elm: ".js-box-image"
      });
    });
  });

}).call(this);

//# sourceMappingURL=editor_image_upload-spec.js.map
