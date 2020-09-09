(function() {
  describe("editor file upload plugin tests", function() {
    var dialog, editor, post, responseData, textarea, triggerFakeUpload;
    textarea = null;
    post = null;
    editor = null;
    dialog = null;
    responseData = null;
    triggerFakeUpload = function(name) {
      var evt, inputFileOrg;
      if (name == null) {
        name = 'foo.doc';
      }
      inputFileOrg = editor.inputFile;
      try {
        editor.inputFile = {
          files: [
            {
              name: name
            }
          ]
        };
        evt = document.createEvent("HTMLEvents");
        evt.initEvent("change", false, true);
        return inputFileOrg.dispatchEvent(evt);
      } finally {
        editor.inputFile = inputFileOrg;
      }
    };
    beforeEach(function() {
      document.body.innerHTML = "<form class=\"js-reply\" action=\".\">\n    <textarea id=\"id_comment\"></textarea>\n    <div class=\"js-box-preview-content\" style=\"display:none;\"></div>\n    <ul>\n        <li><a class=\"js-box-bold\" href=\"#\" title=\"Bold\"></a></li>\n        <li><a class=\"js-box-italic\" href=\"#\" title=\"Italic\"></a></li>\n        <li><a class=\"js-box-list\" href=\"#\" title=\"List\"></a></li>\n        <li><a class=\"js-box-url\" href=\"#\" title=\"URL\"></a></li>\n        <li><a class=\"js-box-image\" href=\"#\" title=\"Image\"></a></li>\n        <li><a class=\"js-box-file\" href=\"#\" title=\"File\"></a></li>\n        <li><a class=\"js-box-poll\" href=\"#\" title=\"Poll\"></a></li>\n        <li><a class=\"js-box-preview\" href=\"#\" title=\"Preview\"></a></li>\n    </ul>\n</form>";
      responseData = {
        url: '/path/foo'
      };
      post = spyOn(global, 'fetch');
      post.and.callFake(function() {
        return {
          then: function(func) {
            var data;
            data = func({
              ok: true,
              json: function() {
                return responseData;
              }
            });
            return {
              then: function(func) {
                func(data);
                return {
                  "catch": function() {}
                };
              }
            };
          }
        };
      });
      editor = stModules.editorFileUpload(document.querySelectorAll('.js-reply'), {
        csrfToken: "foo csrf_token",
        target: "/foo/",
        placeholderText: "foo uploading {name}",
        allowedFileMedia: ".doc,.docx,.pdf"
      })[0];
      textarea = document.querySelector('textarea');
      dialog = spyOn(editor.inputFile, 'click');
      return dialog.and.callFake(function() {});
    });
    it("opens the file choose dialog", function() {
      dialog.calls.reset();
      document.querySelector('.js-box-file').click();
      return expect(dialog).toHaveBeenCalled();
    });
    it("uploads the file", function() {
      var formDataMock;
      post.calls.reset();
      formDataMock = jasmine.createSpyObj('formDataMock', ['append']);
      spyOn(global, "FormData").and.returnValue(formDataMock);
      triggerFakeUpload('foo.doc');
      expect(post.calls.any()).toEqual(true);
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/');
      expect(post.calls.argsFor(0)[1].body).toEqual(formDataMock);
      expect(formDataMock.append).toHaveBeenCalledWith('csrfmiddlewaretoken', 'foo csrf_token');
      return expect(formDataMock.append).toHaveBeenCalledWith('file', {
        name: 'foo.doc'
      });
    });
    it("changes the placeholder on upload success", function() {
      textarea.value = "foobar";
      triggerFakeUpload('foo.doc');
      return expect(textarea.value).toEqual("foobar[foo.doc](/path/foo)");
    });
    it("changes the placeholder on upload error", function() {
      textarea.value = "foobar";
      responseData = {
        error: {
          foo: 'foo error'
        }
      };
      triggerFakeUpload('foo.doc');
      return expect(textarea.value).toEqual('foobar[{"foo":"foo error"}]()');
    });
    it("changes the placeholder on upload failure", function() {
      var log;
      post.calls.reset();
      textarea.value = "foobar";
      post.and.callFake(function() {
        return {
          then: function(func) {
            var err;
            try {
              return func({
                ok: false,
                status: 500,
                statusText: 'foo error'
              });
            } catch (error) {
              err = error;
              return {
                then: function() {
                  return {
                    "catch": function(func) {
                      return func(err);
                    }
                  };
                }
              };
            }
          }
        };
      });
      log = spyOn(console, 'log');
      log.and.callFake(function() {});
      triggerFakeUpload('foo.doc');
      expect(post.calls.any()).toEqual(true);
      expect(textarea.value).toEqual("foobar[error: 500 foo error]()");
      return expect(log.calls.argsFor(0)[0]).toEqual('error: 500 foo error');
    });
    it("checks for default media file extensions if none are provided", function() {
      return expect(editor.inputFile.accept).toEqual(".doc,.docx,.pdf");
    });
    it("checks for custom media file extensions if they are provided", function() {
      editor = stModules.editorFileUpload(document.querySelectorAll('.js-reply'), {
        allowedFileMedia: ".superdoc"
      })[0];
      return expect(editor.inputFile.accept).toEqual(".superdoc");
    });
    return it("has correct meta data", function() {
      return expect(editor.meta).toEqual({
        fieldName: "file",
        tag: "[{text}]({url})",
        elm: ".js-box-file"
      });
    });
  });

}).call(this);

//# sourceMappingURL=editor_file_upload-spec.js.map
