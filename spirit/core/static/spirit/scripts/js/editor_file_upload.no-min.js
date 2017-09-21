
/*
    Markdown editor image upload, should be loaded before $.editor()
    requires: util.js
 */

(function() {
  var $, EditorUpload,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

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
      if (meta == null) {
        meta = null;
      }
      this.openFileDialog = bind(this.openFileDialog, this);
      this.textReplace = bind(this.textReplace, this);
      this.addStatusError = bind(this.addStatusError, this);
      this.addError = bind(this.addError, this);
      this.addFile = bind(this.addFile, this);
      this.buildFormData = bind(this.buildFormData, this);
      this.addPlaceholder = bind(this.addPlaceholder, this);
      this.sendFile = bind(this.sendFile, this);
      this.el = $(el);
      this.options = $.extend({}, this.defaults, options);
      this.meta = $.extend({}, this._meta, meta || {});
      this.formFile = $("<form/>");
      this.inputFile = $("<input/>", {
        type: "file",
        accept: this.options.allowedFileMedia
      }).appendTo(this.formFile);
      this.setUp();
    }

    EditorUpload.prototype.setUp = function() {
      var $boxElm;
      if (window.FormData == null) {
        return;
      }
      this.inputFile.on('change', this.sendFile);
      $boxElm = $(this.meta.elm);
      $boxElm.on('click', this.openFileDialog);
      return $boxElm.on('click', this.stopClick);
    };

    EditorUpload.prototype.sendFile = function() {
      var file, formData, placeholder;
      file = this.inputFile.get(0).files[0];
      placeholder = this.addPlaceholder(file);
      formData = this.buildFormData(file);
      $.ajax({
        url: this.options.target,
        data: formData,
        processData: false,
        contentType: false,
        type: 'POST'
      }).done((function(_this) {
        return function(data) {
          if ("url" in data) {
            return _this.addFile(data, file, placeholder);
          } else {
            return _this.addError(data, placeholder);
          }
        };
      })(this)).fail((function(_this) {
        return function(jqxhr, textStatus, error) {
          return _this.addStatusError(textStatus, error, placeholder);
        };
      })(this)).always((function(_this) {
        return function() {
          return _this.formFile.get(0).reset();
        };
      })(this));
    };

    EditorUpload.prototype.addPlaceholder = function(file) {
      var placeholder;
      placeholder = $.format(this.meta.tag, {
        text: $.format(this.options.placeholderText, {
          name: file.name
        }),
        url: ""
      });
      this.el.val(this.el.val() + placeholder);
      return placeholder;
    };

    EditorUpload.prototype.buildFormData = function(file) {
      var formData;
      formData = new FormData();
      formData.append('csrfmiddlewaretoken', this.options.csrfToken);
      formData.append(this.meta.fieldName, file);
      return formData;
    };

    EditorUpload.prototype.addFile = function(data, file, placeholder) {
      var imageTag;
      imageTag = $.format(this.meta.tag, {
        text: file.name,
        url: data.url
      });
      return this.textReplace(placeholder, imageTag);
    };

    EditorUpload.prototype.addError = function(data, placeholder) {
      var error;
      error = JSON.stringify(data);
      return this.textReplace(placeholder, $.format(this.meta.tag, {
        text: error,
        url: ""
      }));
    };

    EditorUpload.prototype.addStatusError = function(textStatus, error, placeholder) {
      var errorTag;
      errorTag = $.format(this.meta.tag, {
        text: $.format("error: {code} {error}", {
          code: textStatus,
          error: error
        }),
        url: ""
      });
      return this.textReplace(placeholder, errorTag);
    };

    EditorUpload.prototype.textReplace = function(find, replace) {
      this.el.val(this.el.val().replace(find, replace));
    };

    EditorUpload.prototype.openFileDialog = function() {
      this.inputFile.trigger('click');
    };

    EditorUpload.prototype.stopClick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    };

    return EditorUpload;

  })();

  $.fn.extend({
    editor_file_upload: function(options) {
      return this.each(function() {
        if (!$(this).data('plugin_editor_file_upload')) {
          return $(this).data('plugin_editor_file_upload', new EditorUpload(this, options));
        }
      });
    },
    editor_image_upload: function(options) {
      return this.each(function() {
        if (!$(this).data('plugin_editor_image_upload')) {
          return $(this).data('plugin_editor_image_upload', new EditorUpload(this, options, {
            fieldName: "image",
            tag: "![{text}]({url})",
            elm: ".js-box-image"
          }));
        }
      });
    }
  });

}).call(this);
