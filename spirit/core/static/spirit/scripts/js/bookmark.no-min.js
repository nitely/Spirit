
/*
    A library to tell the server how far you have scrolled down.
    requires: waypoints
 */

(function() {
  var $, Bookmark, Mark,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  Mark = (function() {
    function Mark() {
      this.isSending = false;
      this.commentNumber = this._getCommentNumber();
    }

    Mark.prototype._getCommentNumber = function() {
      var commentNumber;
      commentNumber = window.location.hash.split("#c")[1];
      commentNumber = parseInt(commentNumber, 10);
      if (isNaN(commentNumber)) {
        commentNumber = 0;
      } else {
        commentNumber -= 1;
      }
      return commentNumber;
    };

    return Mark;

  })();

  Bookmark = (function() {
    Bookmark.prototype.defaults = {
      csrfToken: "csrf_token",
      target: "target url"
    };

    function Bookmark(el, mark, options) {
      this.sendCommentNumber = bind(this.sendCommentNumber, this);
      this.onWaypoint = bind(this.onWaypoint, this);
      this.el = $(el);
      this.mark = mark;
      this.options = $.extend({}, this.defaults, options);
      this.setUp();
    }

    Bookmark.prototype.setUp = function() {
      return this.el.waypoint(this.onWaypoint, {
        offset: '100%'
      });
    };

    Bookmark.prototype.onWaypoint = function() {
      var newCommentNumber;
      newCommentNumber = this.el.data('number');
      if (newCommentNumber > this.mark.commentNumber) {
        this.mark.commentNumber = newCommentNumber;
        this.sendCommentNumber();
      }
    };

    Bookmark.prototype.sendCommentNumber = function() {
      var sentCommentNumber;
      if (this.mark.isSending) {
        return;
      }
      this.mark.isSending = true;
      sentCommentNumber = this.mark.commentNumber;
      return $.post(this.options.target, {
        csrfmiddlewaretoken: this.options.csrfToken,
        comment_number: this.mark.commentNumber
      }).always((function(_this) {
        return function() {
          _this.mark.isSending = false;
          if (_this.mark.commentNumber > sentCommentNumber) {
            return _this.sendCommentNumber();
          }
        };
      })(this));
    };

    return Bookmark;

  })();

  $.fn.extend({
    bookmark: function(options) {
      var mark;
      mark = new Mark();
      return this.each(function() {
        if (!$(this).data('plugin_bookmark')) {
          return $(this).data('plugin_bookmark', new Bookmark(this, mark, options));
        }
      });
    }
  });

  $.fn.bookmark.Bookmark = Bookmark;

  $.fn.bookmark.Mark = Mark;

}).call(this);
