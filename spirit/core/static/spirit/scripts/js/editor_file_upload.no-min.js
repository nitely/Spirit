
/*
    Markdown editor image upload, should be loaded before $.editor()
    requires: util.js
 */

(function() {
  var EditorUpload, utils,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  utils = stModules.utils;

  EditorUpload = (function() {
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

    function EditorUpload(el, options, meta) {
      if (options == null) {
        options = null;
      }
      if (meta == null) {
        meta = null;
      }
      this.openFileDialog = bind(this.openFileDialog, this);
      this.textReplace = bind(this.textReplace, this);
      this.addError = bind(this.addError, this);
      this.addFile = bind(this.addFile, this);
      this.buildFormData = bind(this.buildFormData, this);
      this.addPlaceholder = bind(this.addPlaceholder, this);
      this.sendFile = bind(this.sendFile, this);
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

    EditorUpload.prototype.setUp = function() {
      this.formFile.appendChild(this.inputFile);
      this.inputFile.addEventListener('change', this.sendFile);
      return this.el.querySelector(this.meta.elm).addEventListener('click', this.openFileDialog);
    };

    EditorUpload.prototype.sendFile = function() {
      var file, formData, headers, placeholder;
      file = this.inputFile.files[0];
      placeholder = this.addPlaceholder(file);
      formData = this.buildFormData(file);
      this.formFile.reset();
      headers = new Headers();
      headers.append("X-Requested-With", "XMLHttpRequest");
      fetch(this.options.target, {
        method: "POST",
        headers: headers,
        credentials: 'same-origin',
        body: formData
      }).then((function(_this) {
        return function(response) {
          if (!response.ok) {
            throw new Error("error: " + response.status + " " + response.statusText);
          }
          return response.json();
        };
      })(this)).then((function(_this) {
        return function(data) {
          if ("url" in data) {
            return _this.addFile(file.name, data.url, placeholder);
          } else {
            return _this.addError(JSON.stringify(data.error), placeholder);
          }
        };
      })(this))["catch"]((function(_this) {
        return function(error) {
          console.log(error.message);
          return _this.addError(error.message, placeholder);
        };
      })(this));
    };

    EditorUpload.prototype.addPlaceholder = function(file) {
      var placeholder;
      placeholder = utils.format(this.meta.tag, {
        text: utils.format(this.options.placeholderText, {
          name: file.name
        }),
        url: ""
      });
      this.textBox.value += placeholder;
      return placeholder;
    };

    EditorUpload.prototype.buildFormData = function(file) {
      var formData;
      formData = new FormData();
      formData.append('csrfmiddlewaretoken', this.options.csrfToken);
      formData.append(this.meta.fieldName, file);
      return formData;
    };

    EditorUpload.prototype.addFile = function(name, url, placeholder) {
      var imageTag;
      imageTag = utils.format(this.meta.tag, {
        text: name,
        url: url
      });
      return this.textReplace(placeholder, imageTag);
    };

    EditorUpload.prototype.addError = function(error, placeholder) {
      return this.textReplace(placeholder, utils.format(this.meta.tag, {
        text: error,
        url: ""
      }));
    };

    EditorUpload.prototype.textReplace = function(find, replace) {
      this.textBox.value = this.textBox.value.replace(find, replace);
    };

    EditorUpload.prototype.openFileDialog = function(e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return this.inputFile.click();
    };

    return EditorUpload;

  })();

  stModules.editorFileUpload = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new EditorUpload(elm, options);
    });
  };

  stModules.editorImageUpload = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new EditorUpload(elm, options, {
        fieldName: "image",
        tag: "![{text}]({url})",
        elm: ".js-box-image"
      });
    });
  };

  stModules.EditorUpload = EditorUpload;

}).call(this);
