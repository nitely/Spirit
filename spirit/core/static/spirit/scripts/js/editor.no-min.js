
/*
    Markdown editor
    requires: marked.js
 */

(function() {
  var $, Editor,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  Editor = (function() {
    Editor.prototype.defaults = {
      boldedText: "bolded text",
      italicisedText: "italicised text",
      listItemText: "list item",
      linkText: "link text",
      linkUrlText: "link url",
      imageText: "image text",
      imageUrlText: "image url",
      pollTitleText: "Title",
      pollChoiceText: "Description"
    };

    function Editor(el, options) {
      this.togglePreview = bind(this.togglePreview, this);
      this.addPoll = bind(this.addPoll, this);
      this.addImage = bind(this.addImage, this);
      this.addUrl = bind(this.addUrl, this);
      this.addList = bind(this.addList, this);
      this.addItalic = bind(this.addItalic, this);
      this.addBold = bind(this.addBold, this);
      this.wrapSelection = bind(this.wrapSelection, this);
      this.el = $(el);
      this.options = $.extend({}, this.defaults, options);
      this.pollCounter = 1;
      this.setUp();
    }

    Editor.prototype.setUp = function() {
      $('.js-box-bold').on('click', this.addBold);
      $('.js-box-italic').on('click', this.addItalic);
      $('.js-box-list').on('click', this.addList);
      $('.js-box-url').on('click', this.addUrl);
      $('.js-box-image').on('click', this.addImage);
      $('.js-box-poll').on('click', this.addPoll);
      return $('.js-box-preview').on('click', this.togglePreview);
    };

    Editor.prototype.wrapSelection = function(preTxt, postTxt, defaultTxt) {
      var postSelection, preSelection, selection;
      preSelection = this.el.val().substring(0, this.el[0].selectionStart);
      selection = this.el.val().substring(this.el[0].selectionStart, this.el[0].selectionEnd);
      postSelection = this.el.val().substring(this.el[0].selectionEnd);
      if (!selection) {
        selection = defaultTxt;
      }
      return this.el.val(preSelection + preTxt + selection + postTxt + postSelection);
    };

    Editor.prototype.addBold = function() {
      this.wrapSelection("**", "**", this.options.boldedText);
      return false;
    };

    Editor.prototype.addItalic = function() {
      this.wrapSelection("*", "*", this.options.italicisedText);
      return false;
    };

    Editor.prototype.addList = function() {
      this.wrapSelection("\n* ", "", this.options.listItemText);
      return false;
    };

    Editor.prototype.addUrl = function() {
      this.wrapSelection("[", "](" + this.options.linkUrlText + ")", this.options.linkText);
      return false;
    };

    Editor.prototype.addImage = function() {
      this.wrapSelection("![", "](" + this.options.imageUrlText + ")", this.options.imageText);
      return false;
    };

    Editor.prototype.addPoll = function() {
      var poll;
      poll = ("\n\n[poll name=" + this.pollCounter + "]\n") + ("# " + this.options.pollTitleText + "\n") + ("1. " + this.options.pollChoiceText + "\n") + ("2. " + this.options.pollChoiceText + "\n") + "[/poll]\n";
      this.wrapSelection("", poll, "");
      this.pollCounter++;
      return false;
    };

    Editor.prototype.togglePreview = function() {
      var $preview;
      $preview = $('.js-box-preview-content');
      this.el.toggle();
      $preview.toggle();
      $preview.html(marked(this.el.val()));
      return false;
    };

    return Editor;

  })();

  $.fn.extend({
    editor: function(options) {
      return this.each(function() {
        if (!$(this).data('plugin_editor')) {
          return $(this).data('plugin_editor', new Editor(this, options));
        }
      });
    }
  });

  $.fn.editor.Editor = Editor;

}).call(this);
