"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Notifications ajax tab
      requires: util.js, tab.js
  */
  var Notification, Tab, utils;
  utils = stModules.utils;
  Tab = stModules.Tab;

  Notification = function () {
    // todo: short-polling (with back-off) and fetch notifications every time
    var Notification = /*#__PURE__*/function () {
      function Notification(el, options) {
        _classCallCheck(this, Notification);

        this.tabSwitch = this.tabSwitch.bind(this);
        this.addNotifications = this.addNotifications.bind(this);
        this.addShowMoreLink = this.addShowMoreLink.bind(this);
        this.addIsEmptyTxt = this.addIsEmptyTxt.bind(this);
        this.addErrorTxt = this.addErrorTxt.bind(this);
        this.ajaxDone = this.ajaxDone.bind(this);
        this.el = el;
        this.options = Object.assign({}, this.defaults, options);
        this.contentElm = document.querySelector(el.dataset.related);
        this.setUp();
      }

      _createClass(Notification, [{
        key: "setUp",
        value: function setUp() {
          return this.el.addEventListener('click', this.tabSwitch);
        }
      }, {
        key: "tabSwitch",
        value: function tabSwitch(e) {
          var _this = this;

          var headers;
          e.preventDefault();
          e.stopPropagation(); // Detach the event so notification are fetched just once,
          // following clicks will show the cached notifications

          this.el.removeEventListener('click', this.tabSwitch);
          headers = new Headers();
          headers.append("X-Requested-With", "XMLHttpRequest");
          fetch(this.options.notificationUrl, {
            method: "GET",
            headers: headers,
            credentials: 'same-origin'
          }).then(function (response) {
            if (!response.ok) {
              throw new Error("error: ".concat(response.status, " ").concat(response.statusText));
            }

            return response.json(); // Promise
          }).then(function (data) {
            if (data.n.length > 0) {
              _this.addNotifications(data.n);

              return _this.addShowMoreLink();
            } else {
              return _this.addIsEmptyTxt();
            }
          }).catch(function (error) {
            console.log(error.message);
            return _this.addErrorTxt(error.message);
          }).then(function () {
            return _this.ajaxDone();
          });
        }
      }, {
        key: "addNotifications",
        value: function addNotifications(notifications) {
          var _this2 = this;

          return notifications.forEach(function (n) {
            var linkElm, txt, txtElm, unreadElm; // todo: actions should be pass in options as an object map

            if (n.action === 1) {
              txt = _this2.options.mentionTxt;
            } else {
              txt = _this2.options.commentTxt;
            }

            linkElm = document.createElement('a');
            linkElm.setAttribute('href', n.url);
            linkElm.textContent = n.title; // Untrusted

            txtElm = document.createElement('div');
            txtElm.innerHTML = utils.format(txt, {
              user: n.user,
              topic: linkElm.outerHTML
            });

            if (!n.is_read) {
              unreadElm = document.createElement('span');
              unreadElm.className = 'row-unread';
              unreadElm.innerHTML = _this2.options.unread;
              txtElm.innerHTML += " ";
              txtElm.appendChild(unreadElm);
            }

            _this2.contentElm.appendChild(txtElm);
          });
        }
      }, {
        key: "addShowMoreLink",
        value: function addShowMoreLink() {
          var showAllContainerElm, showAllLinkElm;
          showAllContainerElm = document.createElement('div');
          showAllLinkElm = document.createElement('a');
          showAllLinkElm.setAttribute('href', this.options.notificationListUrl);
          showAllLinkElm.innerHTML = this.options.showAll;
          showAllContainerElm.appendChild(showAllLinkElm);
          return this.contentElm.appendChild(showAllContainerElm);
        }
      }, {
        key: "addIsEmptyTxt",
        value: function addIsEmptyTxt() {
          var emptyElm;
          emptyElm = document.createElement('div');
          emptyElm.innerHTML = this.options.empty;
          return this.contentElm.appendChild(emptyElm);
        }
      }, {
        key: "addErrorTxt",
        value: function addErrorTxt(message) {
          var ErrorElm;
          ErrorElm = document.createElement('div');
          ErrorElm.textContent = message;
          return this.contentElm.appendChild(ErrorElm);
        }
      }, {
        key: "ajaxDone",
        value: function ajaxDone() {
          this.el.classList.add('js-tab');
          new Tab(this.el);
          return this.el.click();
        }
      }]);

      return Notification;
    }();

    ;
    Notification.prototype.defaults = {
      notificationUrl: "#ajax",
      notificationListUrl: "#show-all",
      mentionTxt: "{user} mention you on {topic}",
      commentTxt: "{user} has commented on {topic}",
      showAll: "Show all",
      empty: "Nothing to show",
      unread: "unread"
    };
    return Notification;
  }.call(this);

  stModules.notification = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new Notification(elm, options);
    });
  };

  stModules.Notification = Notification;
}).call(void 0);