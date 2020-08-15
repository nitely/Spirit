function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      A library to tell the server how far you have scrolled down.
      requires: modules, waypoints
  */
  var Bookmark, Mark;

  Mark = function () {
    var Mark = /*#__PURE__*/function () {
      function Mark(options) {
        _classCallCheck(this, Mark);

        this.canSend = this.canSend.bind(this);
        this.sendMark = this.sendMark.bind(this);
        this.options = Object.assign({}, this.defaults, options);
        this.isSending = false;
        this.commentNumber = this._getCommentNumber();
        this.numberQueued = this.commentNumber;
      }

      _createClass(Mark, [{
        key: "_getCommentNumber",
        value: function _getCommentNumber() {
          var commentNumber;
          commentNumber = window.location.hash.split("#c")[1];
          commentNumber = parseInt(commentNumber, 10); // base 10

          if (isNaN(commentNumber)) {
            commentNumber = 0;
          } else {
            // workaround to always send comment number from hash
            commentNumber -= 1;
          }

          return commentNumber;
        }
      }, {
        key: "canSend",
        value: function canSend(number) {
          Number.isInteger(number) || console.error('not a number');
          return number > this.commentNumber;
        }
      }, {
        key: "sendMark",
        value: function sendMark(number) {
          var _this = this;

          var form, headers;

          if (!this.canSend(number)) {
            return;
          }

          this.numberQueued = number;

          if (this.isSending) {
            return;
          }

          this.isSending = true;
          this.commentNumber = number;
          form = new FormData();
          form.append('csrfmiddlewaretoken', this.options.csrfToken);
          form.append('comment_number', String(number));
          headers = new Headers();
          headers.append("X-Requested-With", "XMLHttpRequest");
          return fetch(this.options.target, {
            method: "POST",
            headers: headers,
            credentials: 'same-origin',
            body: form
          }).then(function (response) {
            return response.ok || console.log({
              status: response.status,
              statusText: response.statusText
            });
          }).catch(function (error) {
            return console.log(error.message);
          }).then(function () {
            _this.isSending = false;
            return _this.sendMark(_this.numberQueued);
          });
        }
      }]);

      return Mark;
    }();

    ; //# This is shared among a set of bookmarks

    Mark.prototype.defaults = {
      csrfToken: "csrf_token",
      target: "target url"
    };
    return Mark;
  }.call(this);

  Bookmark = /*#__PURE__*/function () {
    function Bookmark(el, mark) {
      _classCallCheck(this, Bookmark);

      this._getNumber = this._getNumber.bind(this);
      this.onWaypoint = this.onWaypoint.bind(this);
      this.el = el;
      this.mark = mark;
      this.number = this._getNumber();
      this.waypoint = this._addWaypointListener(el, this.onWaypoint);
    }

    _createClass(Bookmark, [{
      key: "_addWaypointListener",
      value: function _addWaypointListener(elm, handler) {
        return new Waypoint({
          element: elm,
          handler: handler,
          offset: '100%'
        });
      }
    }, {
      key: "_getNumber",
      value: function _getNumber() {
        var number;
        number = parseInt(this.el.dataset.number, 10);
        !isNaN(number) || console.error('comment number is NaN');
        return number;
      }
    }, {
      key: "onWaypoint",
      value: function onWaypoint() {
        this.mark.sendMark(this.number);
      }
    }]);

    return Bookmark;
  }();

  stModules.bookmark = function (elms, options) {
    var mark;
    mark = new Mark(options);
    return Array.from(elms).map(function (elm) {
      return new Bookmark(elm, mark);
    });
  };

  stModules.Bookmark = Bookmark;
  stModules.Mark = Mark;
}).call(this);