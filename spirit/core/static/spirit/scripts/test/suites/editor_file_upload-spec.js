(function() {
  describe("editor file upload plugin tests", function() {
    var data, editorFileUpload, file, inputFile, post, textarea;
    textarea = null;
    editorFileUpload = null;
    data = null;
    inputFile = null;
    file = null;
    post = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('editor.html');
      post = spyOn($, 'ajax');
      post.and.callFake(function(req) {
        var d;
        d = $.Deferred();
        d.resolve(data);
        return d.promise();
      });
      data = {
        url: "/path/file.pdf"
      };
      file = {
        name: "foo.pdf"
      };
      textarea = $('#id_comment').editor_file_upload({
        csrfToken: "foo csrf_token",
        target: "/foo/",
        placeholderText: "foo uploading {name}",
        allowedFileMedia: ".doc,.docx,.pdf"
      });
      editorFileUpload = textarea.first().data('plugin_editor_file_upload');
      return inputFile = editorFileUpload.inputFile;
    });
    it("doesnt break selector chaining", function() {
      expect(textarea).toEqual($('#id_comment'));
      return expect(textarea.length).toEqual(1);
    });
    it("does nothing if the browser is not supported", function() {
      var inputFile2, org_formData, textarea2, trigger;
      org_formData = window.FormData;
      window.FormData = null;
      try {
        $(".js-box-file").off('click');
        textarea2 = $('#id_comment2').editor_file_upload();
        inputFile2 = textarea2.data('plugin_editor_file_upload').inputFile;
        trigger = spyOn(inputFile2, 'trigger');
        $(".js-box-file").trigger('click');
        return expect(trigger).not.toHaveBeenCalled();
      } finally {
        window.FormData = org_formData;
      }
    });
    it("opens the file choose dialog", function() {
      var trigger;
      trigger = spyOn(inputFile, 'trigger');
      $(".js-box-file").trigger('click');
      return expect(trigger).toHaveBeenCalled();
    });
    it("uploads the file", function() {
      var formDataMock;
      expect($.ajax.calls.any()).toEqual(false);
      formDataMock = jasmine.createSpyObj('formDataMock', ['append']);
      spyOn(window, "FormData").and.returnValue(formDataMock);
      spyOn(inputFile, 'get').and.returnValue({
        files: [file]
      });
      inputFile.trigger('change');
      expect($.ajax.calls.any()).toEqual(true);
      expect($.ajax.calls.argsFor(0)).toEqual([
        {
          url: '/foo/',
          data: formDataMock,
          processData: false,
          contentType: false,
          type: 'POST'
        }
      ]);
      expect(formDataMock.append).toHaveBeenCalledWith('csrfmiddlewaretoken', 'foo csrf_token');
      return expect(formDataMock.append).toHaveBeenCalledWith('file', {
        name: 'foo.pdf'
      });
    });
    it("changes the placeholder on upload success", function() {
      textarea.val("foobar");
      spyOn(inputFile, 'get').and.returnValue({
        files: [file]
      });
      inputFile.trigger('change');
      return expect(textarea.val()).toEqual("foobar[foo.pdf](/path/file.pdf)");
    });
    it("changes the placeholder on upload error", function() {
      textarea.val("foobar");
      data = {
        error: {
          foo: "foo error"
        }
      };
      spyOn(inputFile, 'get').and.returnValue({
        files: [file]
      });
      inputFile.trigger('change');
      return expect(textarea.val()).toEqual("foobar[{\"error\":{\"foo\":\"foo error\"}}]()");
    });
    it("changes the placeholder on upload failure", function() {
      var d;
      textarea.val("foobar");
      d = $.Deferred();
      post.and.callFake(function(req) {
        d.reject(null, "foo statusError", "bar error");
        return d.promise();
      });
      spyOn(inputFile, 'get').and.returnValue({
        files: [file]
      });
      inputFile.trigger('change');
      return expect(textarea.val()).toEqual("foobar[error: foo statusError bar error]()");
    });
    it("checks for default media file extensions if none are provided", function() {
      return expect(inputFile[0].outerHTML).toContain(".doc,.docx,.pdf");
    });
    return it("checks for custom media file extensions if they are provided", function() {
      var editorFileUpload3, inputFile3, textarea3;
      textarea3 = $('#id_comment3').editor_file_upload({
        csrfToken: "foo csrf_token",
        target: "/foo/",
        placeholderText: "foo uploading {file_name}",
        allowedFileMedia: [".superdoc"]
      });
      editorFileUpload3 = textarea3.first().data('plugin_editor_file_upload');
      inputFile3 = editorFileUpload3.inputFile;
      expect(inputFile3[0].outerHTML).not.toContain(".doc,.docx,.pdf");
      return expect(inputFile3[0].outerHTML).toContain(".superdoc");
    });
  });

}).call(this);

//# sourceMappingURL=editor_file_upload-spec.js.map
