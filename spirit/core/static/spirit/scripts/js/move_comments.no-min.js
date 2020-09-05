
/*
    Move comments to other topic
 */

(function() {
  var MoveComment, MoveCommentBox,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  MoveCommentBox = (function() {
    MoveCommentBox.prototype.defaults = {
      csrfToken: "csrf_token",
      target: "#post_url"
    };

    function MoveCommentBox(options) {
      this.show = bind(this.show, this);
      this.isHidden = bind(this.isHidden, this);
      this.moveComments = bind(this.moveComments, this);
      this.el = document.querySelector('.js-move-comments-form');
      this.options = Object.assign({}, this.defaults, options);
      this.setUp();
    }

    MoveCommentBox.prototype.setUp = function() {
      return this.el.querySelector('.js-move-comments-button').addEventListener('click', this.moveComments);
    };

    MoveCommentBox.prototype.moveComments = function(e) {
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
      formElm.appendChild(inputTopicIdElm);
      Array.from(document.querySelectorAll('.js-move-comment-checkbox')).forEach(function(elm) {
        return formElm.appendChild(elm.cloneNode(false));
      });
      formElm.submit();
    };

    MoveCommentBox.prototype.isHidden = function() {
      return this.el.style.display === 'none';
    };

    MoveCommentBox.prototype.show = function() {
      this.el.style.display = 'block';
    };

    return MoveCommentBox;

  })();

  MoveComment = (function() {
    function MoveComment(el, box) {
      this.addCommentSelection = bind(this.addCommentSelection, this);
      this.showMoveComments = bind(this.showMoveComments, this);
      this.el = el;
      this.box = box;
      this.setUp();
    }

    MoveComment.prototype.setUp = function() {
      return this.el.addEventListener('click', this.showMoveComments);
    };

    MoveComment.prototype.showMoveComments = function(e) {
      e.preventDefault();
      e.stopPropagation();
      if (this.box.isHidden()) {
        this.box.show();
        this.addCommentSelection();
      }
    };

    MoveComment.prototype.addCommentSelection = function() {
      return Array.from(document.querySelectorAll('.js-move-comment-checkbox-list')).forEach(function(elm) {
        var inputCheckboxElm, liElm;
        liElm = document.createElement('li');
        elm.appendChild(liElm);
        inputCheckboxElm = document.createElement('input');
        inputCheckboxElm.className = 'js-move-comment-checkbox';
        inputCheckboxElm.name = 'comments';
        inputCheckboxElm.type = 'checkbox';
        inputCheckboxElm.value = elm.closest('.js-comment').dataset.pk;
        liElm.appendChild(inputCheckboxElm);
      });
    };

    return MoveComment;

  })();

  stModules.moveComments = function(elms, options) {
    var box;
    box = new MoveCommentBox(options);
    return Array.from(elms).map(function(elm) {
      return new MoveComment(elm, box);
    });
  };

  stModules.MoveCommentBox = MoveCommentBox;

  stModules.MoveComment = MoveComment;

}).call(this);
