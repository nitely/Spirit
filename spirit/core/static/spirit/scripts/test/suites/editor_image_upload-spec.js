(function() {
  describe("editor image upload plugin tests", function() {
    return it("has correct meta data", function() {
      var editor;
      document.body.innerHTML = "<form class=\"js-reply\" action=\".\">\n    <textarea id=\"id_comment\"></textarea>\n    <div class=\"js-box-preview-content\" style=\"display:none;\"></div>\n    <ul>\n        <li><a class=\"js-box-bold\" href=\"#\" title=\"Bold\"></a></li>\n        <li><a class=\"js-box-italic\" href=\"#\" title=\"Italic\"></a></li>\n        <li><a class=\"js-box-list\" href=\"#\" title=\"List\"></a></li>\n        <li><a class=\"js-box-url\" href=\"#\" title=\"URL\"></a></li>\n        <li><a class=\"js-box-image\" href=\"#\" title=\"Image\"></a></li>\n        <li><a class=\"js-box-file\" href=\"#\" title=\"File\"></a></li>\n        <li><a class=\"js-box-poll\" href=\"#\" title=\"Poll\"></a></li>\n        <li><a class=\"js-box-preview\" href=\"#\" title=\"Preview\"></a></li>\n    </ul>\n</form>";
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
