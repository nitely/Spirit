(function() {
  describe("editor plugin tests", function() {
    var editor, textarea;
    textarea = null;
    editor = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('editor.html');
      textarea = $('#id_comment').editor({
        boldedText: "foo bolded text",
        italicisedText: "foo italicised text",
        listItemText: "foo list item",
        linkText: "foo link text",
        linkUrlText: "foo link url",
        imageText: "foo image text",
        imageUrlText: "foo image url"
      });
      return editor = textarea.data('plugin_editor');
    });
    it("doesnt break selector chaining", function() {
      expect(textarea).toEqual($('#id_comment'));
      return expect(textarea.length).toEqual(1);
    });
    it("adds bold", function() {
      $('.js-box-bold').trigger('click');
      return expect(textarea.val()).toEqual("**foo bolded text**");
    });
    it("adds italic", function() {
      $('.js-box-italic').trigger('click');
      return expect(textarea.val()).toEqual("*foo italicised text*");
    });
    it("adds list", function() {
      $('.js-box-list').trigger('click');
      return expect(textarea.val()).toEqual("\n* foo list item");
    });
    it("adds url", function() {
      $('.js-box-url').trigger('click');
      return expect(textarea.val()).toEqual("[foo link text](foo link url)");
    });
    it("adds poll", function() {
      var expected;
      $('.js-box-poll').trigger('click');
      expected = "\n\n[poll name=1]\n# Title\n1. Description\n2. Description\n[/poll]\n";
      expect(textarea.val()).toEqual(expected);
      $('.js-box-poll').trigger('click');
      return expect(textarea.val()).toEqual(expected + "\n\n[poll name=2]\n# Title\n1. Description\n2. Description\n[/poll]\n");
    });
    it("adds image", function() {
      $('.js-box-image').trigger('click');
      return expect(textarea.val()).toEqual("![foo image text](foo image url)");
    });
    it("adds all", function() {
      $('.js-box-bold').trigger('click');
      $('.js-box-italic').trigger('click');
      $('.js-box-list').trigger('click');
      $('.js-box-url').trigger('click');
      $('.js-box-image').trigger('click');
      return $('.js-box-file').trigger('click');
    });
    it("wraps the selected text, bold", function() {
      textarea.val("birfoobar");
      textarea.first()[0].selectionStart = 3;
      textarea.first()[0].selectionEnd = 6;
      $('.js-box-bold').trigger('click');
      return expect(textarea.val()).toEqual("bir**foo**bar");
    });
    it("wraps the selected text, italic", function() {
      textarea.val("birfoobar");
      textarea.first()[0].selectionStart = 3;
      textarea.first()[0].selectionEnd = 6;
      $('.js-box-italic').trigger('click');
      return expect(textarea.val()).toEqual("bir*foo*bar");
    });
    it("wraps the selected text, list", function() {
      textarea.val("birfoobar");
      textarea.first()[0].selectionStart = 3;
      textarea.first()[0].selectionEnd = 6;
      $('.js-box-list').trigger('click');
      return expect(textarea.val()).toEqual("bir\n* foobar");
    });
    it("wraps the selected text, url", function() {
      textarea.val("birfoobar");
      textarea.first()[0].selectionStart = 3;
      textarea.first()[0].selectionEnd = 6;
      $('.js-box-url').trigger('click');
      return expect(textarea.val()).toEqual("bir[foo](foo link url)bar");
    });
    it("wraps the selected text, image", function() {
      textarea.val("birfoobar");
      textarea.first()[0].selectionStart = 3;
      textarea.first()[0].selectionEnd = 6;
      $('.js-box-image').trigger('click');
      return expect(textarea.val()).toEqual("bir![foo](foo image url)bar");
    });
    return it("shows html preview", function() {
      textarea.val("*foo*");
      $('.js-box-preview').trigger('click');
      expect(textarea.is(":visible")).toEqual(false);
      expect($(".js-box-preview-content").is(":visible")).toEqual(true);
      expect($(".js-box-preview-content").html()).toEqual("<p><em>foo</em></p>\n");
      $('.js-box-preview').trigger('click');
      expect(textarea.is(":visible")).toEqual(true);
      return expect($(".js-box-preview-content").is(":visible")).toEqual(false);
    });
  });

}).call(this);

//# sourceMappingURL=editor-spec.js.map
