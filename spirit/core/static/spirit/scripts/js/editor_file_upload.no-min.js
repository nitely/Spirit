function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Markdown editor image upload, should be loaded before $.editor()
      requires: util.js
  */
  var EditorUpload, utils;
  utils = stModules.utils;

  EditorUpload = function () {
    var EditorUpload = /*#__PURE__*/function () {
      function EditorUpload(el) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
        var meta = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;

        _classCallCheck(this, EditorUpload);

        this.sendFile = this.sendFile.bind(this);
        this.addPlaceholder = this.addPlaceholder.bind(this);
        this.buildFormData = this.buildFormData.bind(this);
        this.addFile = this.addFile.bind(this);
        this.addError = this.addError.bind(this);
        this.textReplace = this.textReplace.bind(this);
        this.openFileDialog = this.openFileDialog.bind(this);
        this.el = el;
        this.options = Object.assign({}, this.defaults, options || {});
        this.meta = Object.assign({}, this._meta, meta || {});
        this.textBox = el.querySelector('textarea');
        this.formFile = document.createElement('form');
        this.inputFile = document.createElement('input');
        this.inputFile.type = "file";
        this.inputFile.accept = this.options.allowedFileMedia;
        this.setUp();
      }

      _createClass(EditorUpload, [{
        key: "setUp",
        value: function setUp() {
          this.formFile.appendChild(this.inputFile);
          this.inputFile.addEventListener('change', this.sendFile);
          return this.el.querySelector(this.meta.elm).addEventListener('click', this.openFileDialog);
        }
      }, {
        key: "sendFile",
        value: function sendFile() {
          var _this = this;

          var file, formData, headers, placeholder; // todo: allow many files

          file = this.inputFile.files[0];
          placeholder = this.addPlaceholder(file);
          formData = this.buildFormData(file); // Reset the input fixes uploading the same image twice

          this.formFile.reset();
          headers = new Headers();
          headers.append("X-Requested-With", "XMLHttpRequest");
          fetch(this.options.target, {
            method: "POST",
            headers: headers,
            credentials: 'same-origin',
            body: formData
          }).then(function (response) {
            if (!response.ok) {
              throw new Error("error: ".concat(response.status, " ").concat(response.statusText));
            }

            return response.json(); // Promise
          }).then(function (data) {
            if ("url" in data) {
              return _this.addFile(file.name, data.url, placeholder);
            } else {
              return _this.addError(JSON.stringify(data.error), placeholder);
            }
          }).catch(function (error) {
            console.log(error.message);
            return _this.addError(error.message, placeholder);
          });
        }
      }, {
        key: "addPlaceholder",
        value: function addPlaceholder(file) {
          var placeholder;
          placeholder = utils.format(this.meta.tag, {
            text: utils.format(this.options.placeholderText, {
              name: file.name
            }),
            url: ""
          }); // todo: add at current pointer position

          this.textBox.value += placeholder;
          return placeholder;
        }
      }, {
        key: "buildFormData",
        value: function buildFormData(file) {
          var formData;
          formData = new FormData();
          formData.append('csrfmiddlewaretoken', this.options.csrfToken);
          formData.append(this.meta.fieldName, file);
          return formData;
        }
      }, {
        key: "addFile",
        value: function addFile(name, url, placeholder) {
          var imageTag;
          imageTag = utils.format(this.meta.tag, {
            text: name,
            url: url
          });
          return this.textReplace(placeholder, imageTag);
        }
      }, {
        key: "addError",
        value: function addError(error, placeholder) {
          return this.textReplace(placeholder, utils.format(this.meta.tag, {
            text: error,
            url: ""
          }));
        }
      }, {
        key: "textReplace",
        value: function textReplace(find, replace) {
          // todo: put current pointer position back
          this.textBox.value = this.textBox.value.replace(find, replace);
        }
      }, {
        key: "openFileDialog",
        value: function openFileDialog(e) {
          e.preventDefault();
          e.stopPropagation(); // Avoid default editor button-click handler

          e.stopImmediatePropagation();
          return this.inputFile.click();
        }
      }]);

      return EditorUpload;
    }();

    ;
    EditorUpload.prototype.defaults = {
      csrfToken: "csrf_token",
      target: "target url",
      placeholderText: "uploading {name}",
      allowedFileMedia: ["*/*"]
    };
    EditorUpload.prototype._meta = {
      fieldName: "file",
      tag: "[{text}]({url})",
      elm: ".js-box-file"
    };
    return EditorUpload;
  }.call(this);

  stModules.editorFileUpload = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new EditorUpload(elm, options);
    });
  };

  stModules.editorImageUpload = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new EditorUpload(elm, options, {
        fieldName: "image",
        tag: "![{text}]({url})",
        elm: ".js-box-image"
      });
    });
  };

  stModules.EditorUpload = EditorUpload;
}).call(this);