"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Markdown editor
      requires: modules, marked.js
  */
  var Editor;

  Editor = function () {
    var Editor = /*#__PURE__*/function () {
      function Editor(el, options) {
        _classCallCheck(this, Editor);

        this.wrapSelection = this.wrapSelection.bind(this);
        this.addBold = this.addBold.bind(this);
        this.addItalic = this.addItalic.bind(this);
        this.addList = this.addList.bind(this);
        this.addUrl = this.addUrl.bind(this);
        this.addImage = this.addImage.bind(this);
        this.addPoll = this.addPoll.bind(this);
        this.togglePreview = this.togglePreview.bind(this);
        this.el = el;
        this.options = Object.assign({}, this.defaults, options);
        this.textBox = el.querySelector('textarea');
        this.preview = el.querySelector('.js-box-preview-content');
        this.pollCounter = 1;
        this.isPreviewOn = false;
        this.setUp();
      }

      _createClass(Editor, [{
        key: "setUp",
        value: function setUp() {
          this.el.querySelector('.js-box-bold').addEventListener('click', this.addBold);
          this.el.querySelector('.js-box-italic').addEventListener('click', this.addItalic);
          this.el.querySelector('.js-box-list').addEventListener('click', this.addList);
          this.el.querySelector('.js-box-url').addEventListener('click', this.addUrl);
          this.el.querySelector('.js-box-image').addEventListener('click', this.addImage);
          this.el.querySelector('.js-box-poll').addEventListener('click', this.addPoll);
          return this.el.querySelector('.js-box-preview').addEventListener('click', this.togglePreview);
        }
      }, {
        key: "wrapSelection",
        value: function wrapSelection(preTxt, postTxt, defaultTxt) {
          var pointerLocation, postSelection, preSelection, selection;
          preSelection = this.textBox.value.substring(0, this.textBox.selectionStart);
          selection = this.textBox.value.substring(this.textBox.selectionStart, this.textBox.selectionEnd);
          postSelection = this.textBox.value.substring(this.textBox.selectionEnd);

          if (!selection) {
            selection = defaultTxt;
          }

          this.textBox.value = preSelection + preTxt + selection + postTxt + postSelection; // Set pointer location and give focus back
          // Works well on mobile Chrome and Firefox

          pointerLocation = this.textBox.value.length - postSelection.length;
          this.textBox.setSelectionRange(pointerLocation, pointerLocation);
          return this.textBox.focus();
        }
      }, {
        key: "addBold",
        value: function addBold(e) {
          this.wrapSelection("**", "**", this.options.boldedText);
          return this.stopClick(e);
        }
      }, {
        key: "addItalic",
        value: function addItalic(e) {
          this.wrapSelection("*", "*", this.options.italicisedText);
          return this.stopClick(e);
        }
      }, {
        key: "addList",
        value: function addList(e) {
          this.wrapSelection("\n* ", "", this.options.listItemText);
          return this.stopClick(e);
        }
      }, {
        key: "addUrl",
        value: function addUrl(e) {
          this.wrapSelection("[", "](".concat(this.options.linkUrlText, ")"), this.options.linkText);
          return this.stopClick(e);
        }
      }, {
        key: "addImage",
        value: function addImage(e) {
          this.wrapSelection("![", "](".concat(this.options.imageUrlText, ")"), this.options.imageText);
          return this.stopClick(e);
        }
      }, {
        key: "addPoll",
        value: function addPoll(e) {
          var poll;
          poll = "\n\n[poll name=".concat(this.pollCounter, "]\n") + "# ".concat(this.options.pollTitleText, "\n") + "1. ".concat(this.options.pollChoiceText, "\n") + "2. ".concat(this.options.pollChoiceText, "\n") + "[/poll]\n";
          this.wrapSelection("", poll, ""); // todo: append to current pointer position

          this.pollCounter++;
          return this.stopClick(e);
        }
      }, {
        key: "togglePreview",
        value: function togglePreview(e) {
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
        }
      }, {
        key: "stopClick",
        value: function stopClick(e) {
          e.preventDefault();
          return e.stopPropagation();
        }
      }]);

      return Editor;
    }();

    ;
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
    return Editor;
  }.call(this);

  stModules.editor = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new Editor(elm, options);
    });
  };

  stModules.Editor = Editor;
}).call(void 0);