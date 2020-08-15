"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Move comments to other topic
  */
  var MoveComment, MoveCommentBox;

  MoveCommentBox = function () {
    var MoveCommentBox = /*#__PURE__*/function () {
      function MoveCommentBox(options) {
        _classCallCheck(this, MoveCommentBox);

        this.moveComments = this.moveComments.bind(this);
        this.isHidden = this.isHidden.bind(this);
        this.show = this.show.bind(this);
        this.el = document.querySelector('.move-comments');
        this.options = Object.assign({}, this.defaults, options);
        this.setUp();
      }

      _createClass(MoveCommentBox, [{
        key: "setUp",
        value: function setUp() {
          return this.el.querySelector('.js-move-comments').addEventListener('click', this.moveComments);
        }
      }, {
        key: "moveComments",
        value: function moveComments(e) {
          var formElm, inputCSRFElm, inputTopicIdElm;
          e.preventDefault();
          e.stopPropagation();
          formElm = document.createElement('form');
          formElm.className = 'js-move-comment-form';
          formElm.action = this.options.target;
          formElm.method = 'POST';
          formElm.style.display = 'none';
          document.body.appendChild(formElm);
          inputCSRFElm = document.createElement('input');
          inputCSRFElm.name = 'csrfmiddlewaretoken';
          inputCSRFElm.type = 'hidden';
          inputCSRFElm.value = this.options.csrfToken;
          formElm.appendChild(inputCSRFElm);
          inputTopicIdElm = document.createElement('input');
          inputTopicIdElm.name = 'topic';
          inputTopicIdElm.type = 'text';
          inputTopicIdElm.value = this.el.querySelector('#id_move_comments_topic').value;
          formElm.appendChild(inputTopicIdElm); // Append all selection inputs

          Array.from(document.querySelectorAll('.move-comment-checkbox')).forEach(function (elm) {
            return formElm.appendChild(elm.cloneNode(false));
          });
          formElm.submit();
        }
      }, {
        key: "isHidden",
        value: function isHidden() {
          return this.el.style.display === 'none';
        }
      }, {
        key: "show",
        value: function show() {
          this.el.style.display = 'block';
        }
      }]);

      return MoveCommentBox;
    }();

    ;
    MoveCommentBox.prototype.defaults = {
      csrfToken: "csrf_token",
      target: "#post_url"
    };
    return MoveCommentBox;
  }.call(this);

  MoveComment = /*#__PURE__*/function () {
    //TODO: prefix classes with js-
    function MoveComment(el, box) {
      _classCallCheck(this, MoveComment);

      this.showMoveComments = this.showMoveComments.bind(this);
      this.addCommentSelection = this.addCommentSelection.bind(this);
      this.el = el;
      this.box = box;
      this.setUp();
    }

    _createClass(MoveComment, [{
      key: "setUp",
      value: function setUp() {
        return this.el.addEventListener('click', this.showMoveComments);
      }
    }, {
      key: "showMoveComments",
      value: function showMoveComments(e) {
        e.preventDefault();
        e.stopPropagation();

        if (this.box.isHidden()) {
          this.box.show();
          this.addCommentSelection();
        }
      }
    }, {
      key: "addCommentSelection",
      value: function addCommentSelection() {
        return Array.from(document.querySelectorAll('.comment-date')).forEach(function (elm) {
          var inputCheckboxElm, liElm;
          liElm = document.createElement('li');
          elm.appendChild(liElm);
          inputCheckboxElm = document.createElement('input');
          inputCheckboxElm.className = 'move-comment-checkbox';
          inputCheckboxElm.name = 'comments';
          inputCheckboxElm.type = 'checkbox';
          inputCheckboxElm.value = elm.closest('.comment').dataset.pk;
          liElm.appendChild(inputCheckboxElm);
        });
      }
    }]);

    return MoveComment;
  }();

  stModules.moveComments = function (elms, options) {
    var box;
    box = new MoveCommentBox(options);
    return Array.from(elms).map(function (elm) {
      return new MoveComment(elm, box);
    });
  };

  stModules.MoveCommentBox = MoveCommentBox;
  stModules.MoveComment = MoveComment;
}).call(void 0);