function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Post likes via Ajax
      requires: modules, util.js
  */
  var Like, utils;
  utils = stModules.utils;

  Like = function () {
    var Like = /*#__PURE__*/function () {
      function Like(el, options) {
        _classCallCheck(this, Like);

        this.sendLike = this.sendLike.bind(this);
        this.addLike = this.addLike.bind(this);
        this.removeLike = this.removeLike.bind(this);
        this.apiError = this.apiError.bind(this);
        this.el = el;
        this.options = Object.assign({}, this.defaults, options);
        this.isSending = false;
        this.setUp();
      }

      _createClass(Like, [{
        key: "setUp",
        value: function setUp() {
          return this.el.addEventListener('click', this.sendLike);
        }
      }, {
        key: "sendLike",
        value: function sendLike(e) {
          var _this = this;

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
          }).then(function (response) {
            if (!response.ok) {
              throw new Error("error: ".concat(response.status, " ").concat(response.statusText));
            }

            return response.json(); // Promise
          }).then(function (data) {
            if (data.url_delete) {
              return _this.addLike(data.url_delete);
            } else if (data.url_create) {
              return _this.removeLike(data.url_create);
            } else {
              return _this.apiError();
            }
          }).catch(function (error) {
            console.log(error.message);
            return _this.apiError();
          }).then(function () {
            return _this.isSending = false;
          });
        }
      }, {
        key: "addLike",
        value: function addLike(urlDelete) {
          this.el.setAttribute('href', urlDelete);
          this.el.dataset.count = String(parseInt(this.el.dataset.count, 10) + 1);
          return this.el.innerHTML = utils.format(this.options.removeLikeText, {
            count: this.el.dataset.count
          });
        }
      }, {
        key: "removeLike",
        value: function removeLike(urlCreate) {
          this.el.setAttribute('href', urlCreate);
          this.el.dataset.count = String(parseInt(this.el.dataset.count, 10) - 1);
          return this.el.innerHTML = utils.format(this.options.likeText, {
            count: this.el.dataset.count
          });
        }
      }, {
        key: "apiError",
        value: function apiError() {
          return this.el.textContent = "api error";
        }
      }]);

      return Like;
    }();

    ;
    Like.prototype.defaults = {
      csrfToken: "csrf_token",
      likeText: "like ({count})",
      removeLikeText: "remove like ({count})"
    };
    return Like;
  }.call(this);

  stModules.like = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new Like(elm, options);
    });
  };

  stModules.Like = Like;
}).call(this);