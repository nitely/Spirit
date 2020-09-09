(function() {
  describe("editor plugin tests", function() {
    var editor, textarea;
    textarea = null;
    editor = null;
    beforeEach(function() {
      document.body.innerHTML = "<form class=\"js-reply\" action=\".\">\n    <textarea id=\"id_comment\"></textarea>\n    <div class=\"js-box-preview-content\" style=\"display:none;\"></div>\n    <ul>\n        <li><a class=\"js-box-bold\" href=\"#\" title=\"Bold\"></a></li>\n        <li><a class=\"js-box-italic\" href=\"#\" title=\"Italic\"></a></li>\n        <li><a class=\"js-box-list\" href=\"#\" title=\"List\"></a></li>\n        <li><a class=\"js-box-url\" href=\"#\" title=\"URL\"></a></li>\n        <li><a class=\"js-box-image\" href=\"#\" title=\"Image\"></a></li>\n        <li><a class=\"js-box-file\" href=\"#\" title=\"File\"></a></li>\n        <li><a class=\"js-box-poll\" href=\"#\" title=\"Poll\"></a></li>\n        <li><a class=\"js-box-preview\" href=\"#\" title=\"Preview\"></a></li>\n    </ul>\n</form>";
      editor = stModules.editor(document.querySelectorAll('.js-reply'), {
        boldedText: "foo bolded text",
        italicisedText: "foo italicised text",
        listItemText: "foo list item",
        linkText: "foo link text",
        linkUrlText: "foo link url",
        imageText: "foo image text",
        imageUrlText: "foo image url"
      })[0];
      return textarea = document.querySelector('textarea');
    });
    it("adds bold", function() {
      document.querySelector('.js-box-bold').click();
      return expect(textarea.value).toEqual("**foo bolded text**");
    });
    it("adds italic", function() {
      document.querySelector('.js-box-italic').click();
      return expect(textarea.value).toEqual("*foo italicised text*");
    });
    it("adds list", function() {
      document.querySelector('.js-box-list').click();
      return expect(textarea.value).toEqual("\n* foo list item");
    });
    it("adds url", function() {
      document.querySelector('.js-box-url').click();
      return expect(textarea.value).toEqual("[foo link text](foo link url)");
    });
    it("adds poll", function() {
      var expected;
      document.querySelector('.js-box-poll').click();
      expected = "\n\n[poll name=1]\n# Title\n1. Description\n2. Description\n[/poll]\n";
      expect(textarea.value).toEqual(expected);
      document.querySelector('.js-box-poll').click();
      return expect(textarea.value).toEqual(expected + "\n\n[poll name=2]\n# Title\n1. Description\n2. Description\n[/poll]\n");
    });
    it("adds image", function() {
      document.querySelector('.js-box-image').click();
      return expect(textarea.value).toEqual("![foo image text](foo image url)");
    });
    it("adds all", function() {
      document.querySelector('.js-box-bold').click();
      document.querySelector('.js-box-italic').click();
      document.querySelector('.js-box-list').click();
      document.querySelector('.js-box-url').click();
      document.querySelector('.js-box-image').click();
      document.querySelector('.js-box-file').click();
      return expect(textarea.value).toEqual("**foo bolded text***foo italicised text*" + "\n* foo list item[foo link text](foo link url)![foo image text](foo image url)");
    });
    it("wraps the selected text, bold", function() {
      textarea.value = "birfoobar";
      textarea.selectionStart = 3;
      textarea.selectionEnd = 6;
      document.querySelector('.js-box-bold').click();
      return expect(textarea.value).toEqual("bir**foo**bar");
    });
    it("wraps the selected text, italic", function() {
      textarea.value = "birfoobar";
      textarea.selectionStart = 3;
      textarea.selectionEnd = 6;
      document.querySelector('.js-box-italic').click();
      return expect(textarea.value).toEqual("bir*foo*bar");
    });
    it("wraps the selected text, list", function() {
      textarea.value = "birfoobar";
      textarea.selectionStart = 3;
      textarea.selectionEnd = 6;
      document.querySelector('.js-box-list').click();
      return expect(textarea.value).toEqual("bir\n* foobar");
    });
    it("wraps the selected text, url", function() {
      textarea.value = "birfoobar";
      textarea.selectionStart = 3;
      textarea.selectionEnd = 6;
      document.querySelector('.js-box-url').click();
      return expect(textarea.value).toEqual("bir[foo](foo link url)bar");
    });
    return it("wraps the selected text, image", function() {
      textarea.value = "birfoobar";
      textarea.selectionStart = 3;
      textarea.selectionEnd = 6;
      document.querySelector('.js-box-image').click();
      return expect(textarea.value).toEqual("bir![foo](foo image url)bar");
    });

    /*
    it "shows html preview", ->
        textarea.value = "*foo*"
        document.querySelector('.js-box-preview').click()
        expect(textarea.style.display).toEqual('none')
        expect(document.querySelector('.js-box-preview-content').style.display).toEqual('block')
        expect(document.querySelector('.js-box-preview-content').innerHTML).toEqual(
          "<p><em>foo</em></p>\n")
    
         * clicking again should hide the preview and show the textarea
        document.querySelector('.js-box-preview').click()
        expect(textarea.style.display).toEqual('block')
        expect(document.querySelector('.js-box-preview-content').style.display).toEqual('none')
     */
  });

}).call(this);

//# sourceMappingURL=editor-spec.js.map
