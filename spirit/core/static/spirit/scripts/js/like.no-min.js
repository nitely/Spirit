
/*
    Post likes via Ajax
    requires: util.js
 */

(function() {
  var $, Like,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  Like = (function() {
    Like.prototype.defaults = {
      csrfToken: "csrf_token",
      likeText: "like ({count})",
      removeLikeText: "remove like ({count})"
    };

    function Like(el, options) {
      this.apiError = bind(this.apiError, this);
      this.removeLike = bind(this.removeLike, this);
      this.addLike = bind(this.addLike, this);
      this.sendLike = bind(this.sendLike, this);
      this.el = $(el);
      this.options = $.extend({}, this.defaults, options);
      this.isSending = false;
      this.setUp();
    }

    Like.prototype.setUp = function() {
      this.el.on('click', this.sendLike);
      return this.el.on('click', this.stopClick);
    };

    Like.prototype.sendLike = function() {
      var post;
      if (this.isSending) {
        return;
      }
      this.isSending = true;
      post = $.post(this.el.attr('href'), {
        csrfmiddlewaretoken: this.options.csrfToken
      });
      post.done((function(_this) {
        return function(data) {
          if (data.url_delete) {
            return _this.addLike(data);
          } else if (data.url_create) {
            return _this.removeLike(data);
          } else {
            return _this.apiError();
          }
        };
      })(this));
      post.always((function(_this) {
        return function() {
          return _this.isSending = false;
        };
      })(this));
    };

    Like.prototype.addLike = function(data) {
      var count, removeLikeText;
      this.el.attr('href', data.url_delete);
      count = this.el.data('count');
      count += 1;
      this.el.data('count', count);
      removeLikeText = $.format(this.options.removeLikeText, {
        count: count
      });
      window.location.reload();
      return this.el.text(removeLikeText);
    };

    Like.prototype.removeLike = function(data) {
      var count, likeText;
      this.el.attr('href', data.url_create);
      count = this.el.data('count');
      count -= 1;
      this.el.data('count', count);
      likeText = $.format(this.options.likeText, {
        count: count
      });
      window.location.reload();
      return this.el.text(likeText);
    };

    Like.prototype.apiError = function() {
      return this.el.text("api error");
    };

    Like.prototype.stopClick = function(e) {
      e.preventDefault();
      e.stopPropagation();
    };

    return Like;

  })();

  $.fn.extend({
    like: function(options) {
      return this.each(function() {
        if (!$(this).data('plugin_like')) {
          return $(this).data('plugin_like', new Like(this, options));
        }
      });
    }
  });

  $.fn.like.Like = Like;

}).call(this);
