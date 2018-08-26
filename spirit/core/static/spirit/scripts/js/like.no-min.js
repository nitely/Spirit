
/*
    Post likes via Ajax
    requires: modules, util.js
 */

(function() {
  var Like, utils,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  utils = stModules.utils;

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
      this.el = el;
      this.options = Object.assign({}, this.defaults, options);
      this.isSending = false;
      this.setUp();
    }

    Like.prototype.setUp = function() {
      return this.el.addEventListener('click', this.sendLike);
    };

    Like.prototype.sendLike = function(e) {
      var formData, headers;
      e.preventDefault();
      e.stopPropagation();
      if (this.isSending) {
        return;
      }
      this.isSending = true;
      formData = new FormData();
      formData.append('csrfmiddlewaretoken', this.options.csrfToken);
      headers = new Headers();
      headers.append("X-Requested-With", "XMLHttpRequest");
      fetch(this.el.getAttribute('href'), {
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
          if (data.url_delete) {
            return _this.addLike(data.url_delete);
          } else if (data.url_create) {
            return _this.removeLike(data.url_create);
          } else {
            return _this.apiError();
          }
        };
      })(this))["catch"]((function(_this) {
        return function(error) {
          console.log(error.message);
          return _this.apiError();
        };
      })(this)).then((function(_this) {
        return function() {
          return _this.isSending = false;
        };
      })(this));
    };

    Like.prototype.addLike = function(urlDelete) {
      this.el.setAttribute('href', urlDelete);
      this.el.dataset.count = String(parseInt(this.el.dataset.count, 10) + 1);
      return this.el.innerHTML = utils.format(this.options.removeLikeText, {
        count: this.el.dataset.count
      });
    };

    Like.prototype.removeLike = function(urlCreate) {
      this.el.setAttribute('href', urlCreate);
      this.el.dataset.count = String(parseInt(this.el.dataset.count, 10) - 1);
      return this.el.innerHTML = utils.format(this.options.likeText, {
        count: this.el.dataset.count
      });
    };

    Like.prototype.apiError = function() {
      return this.el.textContent = "api error";
    };

    return Like;

  })();

  stModules.like = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new Like(elm, options);
    });
  };

  stModules.Like = Like;

}).call(this);
