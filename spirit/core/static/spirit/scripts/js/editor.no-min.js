
/*
    Markdown editor
    requires: modules, marked.js
 */

(function() {
  var Editor,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  Editor = (function() {
    Editor.prototype.defaults = {
      replyButtons: [],
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
      this.replyButton = bind(this.replyButton, this);
      this.togglePreview = bind(this.togglePreview, this);
      this.addPoll = bind(this.addPoll, this);
      this.addImage = bind(this.addImage, this);
      this.addUrl = bind(this.addUrl, this);
      this.addList = bind(this.addList, this);
      this.addItalic = bind(this.addItalic, this);
      this.addBold = bind(this.addBold, this);
      this.wrapSelection = bind(this.wrapSelection, this);
      this.el = el;
      this.options = Object.assign({}, this.defaults, options);
      this.textBox = el.querySelector('textarea');
      this.preview = el.querySelector('.js-box-preview-content');
      this.pollCounter = 1;
      this.isPreviewOn = false;
      this.setUp();
    }

    Editor.prototype.setUp = function() {
      var elm, i, len, ref, results;
      this.el.querySelector('.js-box-bold').addEventListener('click', this.addBold);
      this.el.querySelector('.js-box-italic').addEventListener('click', this.addItalic);
      this.el.querySelector('.js-box-list').addEventListener('click', this.addList);
      this.el.querySelector('.js-box-url').addEventListener('click', this.addUrl);
      this.el.querySelector('.js-box-image').addEventListener('click', this.addImage);
      this.el.querySelector('.js-box-poll').addEventListener('click', this.addPoll);
      this.el.querySelector('.js-box-preview').addEventListener('click', this.togglePreview);
      ref = this.options.replyButtons;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        elm = ref[i];
        results.push(elm.addEventListener('click', this.replyButton));
      }
      return results;
    };

    Editor.prototype.wrapSelection = function(preTxt, postTxt, defaultTxt) {
      var pointerLocation, postSelection, preSelection, selection;
      preSelection = this.textBox.value.substring(0, this.textBox.selectionStart);
      selection = this.textBox.value.substring(this.textBox.selectionStart, this.textBox.selectionEnd);
      postSelection = this.textBox.value.substring(this.textBox.selectionEnd);
      if (!selection) {
        selection = defaultTxt;
      }
      this.textBox.value = preSelection + preTxt + selection + postTxt + postSelection;
      pointerLocation = this.textBox.value.length - postSelection.length;
      this.textBox.setSelectionRange(pointerLocation, pointerLocation);
      return this.textBox.focus();
    };

    Editor.prototype.addBold = function(e) {
      this.wrapSelection("**", "**", this.options.boldedText);
      return this.stopClick(e);
    };

    Editor.prototype.addItalic = function(e) {
      this.wrapSelection("*", "*", this.options.italicisedText);
      return this.stopClick(e);
    };

    Editor.prototype.addList = function(e) {
      this.wrapSelection("\n* ", "", this.options.listItemText);
      return this.stopClick(e);
    };

    Editor.prototype.addUrl = function(e) {
      this.wrapSelection("[", "](" + this.options.linkUrlText + ")", this.options.linkText);
      return this.stopClick(e);
    };

    Editor.prototype.addImage = function(e) {
      this.wrapSelection("![", "](" + this.options.imageUrlText + ")", this.options.imageText);
      return this.stopClick(e);
    };

    Editor.prototype.addPoll = function(e) {
      var poll;
      poll = ("\n\n[poll name=" + this.pollCounter + "]\n") + ("# " + this.options.pollTitleText + "\n") + ("1. " + this.options.pollChoiceText + "\n") + ("2. " + this.options.pollChoiceText + "\n") + "[/poll]\n";
      this.wrapSelection("", poll, "");
      this.pollCounter++;
      return this.stopClick(e);
    };

    Editor.prototype.togglePreview = function(e) {
      if (this.isPreviewOn) {
        this.isPreviewOn = false;
        this.textBox.style.display = 'block';
        this.preview.style.display = 'none';
      } else {
        this.isPreviewOn = true;
        this.textBox.style.display = 'none';
        this.preview.style.display = 'block';
        this.preview.innerHTML = marked(this.textBox.value);
      }
      return this.stopClick(e);
    };

    Editor.prototype.replyButton = function(e) {
      window.location.hash = 'reply';
      this.wrapSelection("", ", ", e.currentTarget.getAttribute('data'));
      return this.stopClick(e);
    };

    Editor.prototype.stopClick = function(e) {
      e.preventDefault();
      return e.stopPropagation();
    };

    return Editor;

  })();

  stModules.editor = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new Editor(elm, options);
    });
  };

  stModules.Editor = Editor;

}).call(this);
